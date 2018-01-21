__author__ = 'Campbell Bartlett'

import bottle
import interface

import os

app = bottle.Bottle()

@app.route('/')
def root():\

    session = interface.open_sessions_data()

    conn = interface.sqlite3.connect('stocktake/session.' + session + '.db')

    locationNames = interface.get_location_names(conn)

    safeNames = []

    for name in locationNames:
        safeNames.append(interface.sanitize_html(name))

    return bottle.template('index.tpl', locationNames=locationNames, safeNames=safeNames)

@app.route('/new')
def new():

    session = interface.open_sessions_data()

    newsession = interface.start_next_session(session)

    newsessionstring = str("%03d" % newsession)

    conn = interface.sqlite3.connect('stocktake/session.%03s.db' % newsessionstring)

    interface.create_db(conn)

    interface.add_locations_to_database(conn)

    interface.add_items_to_database(conn)

    bottle.redirect('/')

@app.post("/end")
def saveData():

    session = interface.open_sessions_data()

    conn = interface.sqlite3.connect('stocktake/session.' + session + '.db')

    data = bottle.request.body.read()

    data = str(data, 'UTF-8')

    split = str.split(data, '=')

    date = split[1]

    dateTime = interface.convert_str_to_dateTime(date)

    wrinNos = interface.get_wrinNo_list(conn)

    xml = interface.start_xml(dateTime, session)

    for num in wrinNos:
        xml = interface.add_item_to_xml(xml, num, conn)

    xml = interface.end_xml(xml)

    with open("output/session." + session, "w") as text_file:
        print(xml, file=text_file)

    bottle.redirect('/end')

@app.route('/end')
def root():

    return bottle.template("end.tpl")

@app.post('/area/<area>')
def add_data(area):

    session = interface.open_sessions_data()

    conn = interface.sqlite3.connect('stocktake/session.' + session + '.db')

    formData = bottle.request.body.read()

    interface.add_form_data_to_database(area, formData, conn)

    bottle.redirect('/area/' + area)


@app.route('/static/<filename:path>')
def static(filename):

    return bottle.static_file(filename=filename, root='static')

@app.route('/area/<area>')
def area(area):

    session = interface.open_sessions_data()

    conn = interface.sqlite3.connect('stocktake/session.' + session + '.db')

    wrinNos = interface.get_items_for_location(conn, area)

    itemAttrib = []

    for num in wrinNos:

        itemAttrib.append((interface.item_data_from_wrinNo(conn, num, area)))

    return bottle.template('area.tpl', itemAttrib=itemAttrib, area=area)

if __name__ == "__main__":

    '''interface.create_db(conn)

    interface.add_locations_to_database(conn)

    interface.add_items_to_database(conn)'''

    app.run(host='', port=8080, debug=True)

    input("Press enter to exit")