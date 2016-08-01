from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
from sqlalchemy import create_engine
from sqlalchemy.sql import select
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem
engine = create_engine('sqlite:///restaurantmenu.db')
conn = engine.connect()
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

class webserverHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		try:
			if self.path.endswith("/restaurants"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				restaurants = session.query(Restaurant).all()

				output = ""
				output += "<html><body>"
				output += "<h1>Restaurants</h1>"
				for restaurant in restaurants:
					output += "<div class='restaurant'>"
					output += "<h2>" + restaurant.name + "</h2>"
					output += "<a href='/restaurant/" + str(restaurant.id) + "/edit'><h3>Edit</h3></a>"
					output += "<a href='/restaurant/" + str(restaurant.id) + "/delete'><h3>Delete</h3></a>"
					output += "<br>"
				output += "<a href='/restaurants/new'><h2>Create a restaurant</h2></a>"
				output += "</body></html>"
				self.wfile.write(output)

				return

			if self.path.endswith("/restaurants/new"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				output = ""
				output += "<html><body>"
				output += "<h2>What's the name of the new restaurant?</h2>"
				output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/new'>"
				output += "<input name='restaurant-name' type='text'><input type='submit' value='Submit'>"
				output += "</form></body></html>"
				self.wfile.write(output)

				return

			if self.path.endswith("/edit"):
				restaurant_id = int(self.path[12:-5])
				q = session.query(Restaurant).filter_by(id=restaurant_id).one()
				if q != []:
					self.send_response(200)
					self.send_header('Content-type', 'text/html')
					self.end_headers()
					output = ""
					output += "<html><body>"
					output += "<h2>Enter a new name for " + q.name + ":</h2>"
					output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/edit'>"
					output += "<input name='restaurant-name' type='text'>"
					output += "<input type='hidden' name='restaurant-id' value='" + str(q.id) + "'>"
					output += "<input type='submit' value='Submit'>"
					output += "</form></body></html>"
					self.wfile.write(output)

				return


			if self.path.endswith("/delete"):
				restaurant_id = int(self.path[12:-7])
				q = session.query(Restaurant).filter_by(id=restaurant_id).one()
				if q != []:
					output = ""
					output += "<html><body>"
					output += "<h2>Are you sure you want to delete " + q.name + "?</h2>"
					output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/delete'>"
					output += "<input type='hidden' name='restaurant-id' value='" + str(q.id) + "'>"
					output += "<input type='submit' value='I&#8217;m sure'>"
					output += "</form></body></html>"
					self.wfile.write(output)

				return

		except IOError:
			self.send.error(404, "File Not Found %s" % self.path)

	def do_POST(self):
		try:
			if self.path.endswith("/restaurants/new"):

				ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
				if ctype == 'multipart/form-data':
					fields = cgi.parse_multipart(self.rfile, pdict)
					restaurantName = fields.get('restaurant-name')[0]
					newRestaurant = Restaurant(name = restaurantName)
					session.add(newRestaurant)
					session.commit()

				self.send_response(301)
				self.send_header('Content-type', 'text/html')
				self.send_header('Location', '/restaurants')
				self.end_headers()

				return

			if self.path.endswith("/restaurants/edit"):

				ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
				if ctype == 'multipart/form-data':
					fields = cgi.parse_multipart(self.rfile, pdict)
					restaurantName = fields.get('restaurant-name')[0]
					restaurantId = fields.get('restaurant-id')[0]
					res_to_change = session.query(Restaurant).filter_by(id=restaurantId).first()
					res_to_change.name = restaurantName
					session.commit()

				self.send_response(301)
				self.send_header('Content-type', 'text/html')
				self.send_header('Location', '/restaurants')
				self.end_headers()

				return

			if self.path.endswith("/restaurants/delete"):

				ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
				if ctype == 'multipart/form-data':
					fields = cgi.parse_multipart(self.rfile, pdict)
					restaurantId = fields.get('restaurant-id')[0]
					res_to_delete = session.query(Restaurant).filter_by(id=restaurantId).first()
					restaurantName = res_to_delete.name
					session.delete(res_to_delete)
					session.commit()

				self.send_response(301)
				self.send_header('Content-type', 'text/html')
				self.send_header('Location', '/restaurants')
				self.end_headers()
				
				return


		except:
			pass

def main():
	try:
		port = 8080
		server = HTTPServer(('',port), webserverHandler)
		print "Web server running on port %s" % port
		server.serve_forever()


	except KeyboardInterrupt:
		print "Stopping web server..."
		server.socket.close()


if __name__ == '__main__':
	main()