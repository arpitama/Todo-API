
from flask import Flask
from flask_restful import Api,Resource,reqparse,abort,fields,marshal_with
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

app=Flask(__name__)
api=Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']='False'
db = SQLAlchemy(app)


class TodoModel(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(100),nullable=False)
    description=db.Column(db.String(300),nullable=False)
    date=db.Column(db.String(20),nullable=False)

    def __repr__(self):
        return f"TODO(id = {self.id}, title = {self.title} , desc={self.description} , date={self.date})"


db.create_all()

todos_put_args=reqparse.RequestParser()
todos_put_args.add_argument("title",type=str,help="Title of the todo",required=True)
todos_put_args.add_argument("description",type=str,help="Description of the todo")

todos_update_args=reqparse.RequestParser()
todos_update_args.add_argument("title",type=str,help="Title of the todo")
todos_update_args.add_argument("description",type=str,help="Description of the todo")



resource_fields = {
	'id': fields.Integer,
	'title': fields.String,
	'description': fields.String,
	'date': fields.String,
}


     

class Todo(Resource):
    @marshal_with(resource_fields)
    def get(self,tid):
        result=TodoModel.query.filter_by(id=tid).first()
        if not result:
            abort(404, message="Could not find todo with that id")
        return result

    @marshal_with(resource_fields)
    def post(self,tid):
        args = todos_put_args.parse_args()
        result = TodoModel.query.filter_by(id=tid).first()
        if result:
            abort(409, message="id already taken !! use another id")
        todoitem = TodoModel(id=tid, title=args['title'], description=args['description'], date=str(int(datetime.timestamp(datetime.utcnow()))))
        db.session.add(todoitem)
        db.session.commit()
        return todoitem,201

    @marshal_with(resource_fields)
    def put(self,tid):
        args=todos_update_args.parse_args()
        result=TodoModel.query.filter_by(id=tid).first()
        if not result:
            abort(404,message="Todo does not exist")
        if args['title']:
            result.title=args['title']
        if args['description']:
            result.description=args['description']
        result.date=str(int(datetime.timestamp(datetime.utcnow())))
        db.session.commit()
        return result
    
    def delete(self,tid):
        result=TodoModel.query.filter_by(id=tid).first()
        if not result:
            abort(404,message="Todo does not exist")
        db.session.delete(result)
        db.session.commit()
        return '',204


class AllTodos(Resource):
    @marshal_with(resource_fields)
    def get(self):
        result=TodoModel.query.order_by(TodoModel.id).all()
        return result

api.add_resource(Todo,"/todos/<int:tid>")
api.add_resource(AllTodos,"/alltodos")

if __name__=="__main__":
    app.run(debug=True)