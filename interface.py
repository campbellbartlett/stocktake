import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup

from datetime import datetime

import urllib.parse

import sqlite3

tree = ET.parse('QMAExInventory.xml')
root = tree.getroot()

def open_sessions_data():

    fileName = "sessions/sessions.sessioninfo"

    sessionsRead = open(fileName, 'r')

    for i in sessionsRead:
        session = int(i)

    sessionString = str('%03d') % session

    return sessionString

def start_next_session(session):

    fileName = "sessions/sessions.sessioninfo"

    sessionsAppend = open(fileName, 'a')

    next = int(session) + 1

    sessionsAppend.write(str('\n%03d') % next)

    return int(session) + 1

def convert_str_to_dateTime(string):

    date = datetime.strptime(string, '%Y-%m-%d')

    return(date)


def create_db(db):
    cur = db.cursor()

    sql = """
    DROP TABLE IF EXISTS locations;
    CREATE TABLE locations (
        description text,
        locID numeric unique primary key,
        locOrder numeric
    );
    DROP TABLE IF EXISTS items;
    CREATE TABLE items (
        wrinNo numeric unique primary key,
        status text,
        uom text,
        caseUnits numeric,
        sleeveUnits numeric,
        freq text,
        name text
    );
    DROP TABLE IF EXISTS count;
    CREATE TABLE count (
        countID numeric primary key,
        locID numeric,
        wrinNo numeric,
        caseCount numeric DEFAULT -1,
        sleeveCount numeric DEFAULT -1,
        looseCount numeric DEFAULT -1,
        countOrder numeric,
        FOREIGN KEY (locID) references locations(locID)
        FOREIGN KEY (wrinNo) references items(wrinNo)
    );
    DROP TABLE IF EXISTS session;
    CREATE TABLE session (
        sessionID numeric,
        timeStamp numeric DEFAULT (datetime('now', 'localtime'))
    );
    INSERT INTO session (sessionID)
    VALUES (1);
"""

    cur.executescript(sql)
    db.commit()


def add_locations_to_database(db):
    cur = db.cursor()

    locations = root.findall('Locations/')

    for location in locations:
        description = location.get('description')
        locID = location.get('locid')
        locOrder = location.get('Order')

        sql = """
        INSERT INTO locations (description, locID, locOrder)
        VALUES (?, ?, ?)
        """

        cur.execute(sql, (description, locID, locOrder))
        db.commit()


def add_items_to_database(db):
    cur = db.cursor()

    items = root.findall('items/')

    for item in items:
        wrinNo = item.get('id')
        status = item.get('status')
        uom = item.get('uom')
        caseUnits = item.get('caseunits')
        sleeveUnits = item.get('sleeveunits')
        freq = item.get('freq')
        name = item.get('name')

        sql = """
        INSERT INTO items (wrinNo, status, uom, caseUnits, sleeveUnits, freq, name)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """

        itemLocations = item.iter("Location")

        add_item_and_locations_to_count_table(db, itemLocations, wrinNo)

        cur.execute(sql, (wrinNo, status, uom, caseUnits, sleeveUnits, freq, name))
        db.commit()


def add_item_and_locations_to_count_table(db, itemLocation, wrinNo):
    cur = db.cursor()

    for location in itemLocation:
        locID = location.get('locid')

        sql = """
        SELECT countID FROM count
        WHERE countID = (SELECT MAX(countID) FROM count)
        """

        cur.execute(sql)
        lastCountID = cur.fetchone()
        if lastCountID:
            count = lastCountID[0] + 1
        else:
            count = 0

        sql = """
        INSERT INTO count (locID, wrinNo, countID)
        VALUES (?, ?, ?)
            """

        cur.execute(sql, (locID, wrinNo, count))
        db.commit()


def get_location_names(db):
    cur = db.cursor()

    sql = """
    SELECT description
    FROM locations
    """

    cur.execute(sql)

    result = cur.fetchall()

    locationNames = []

    for name in result:
        locationNames.append(name[0])

    return locationNames


def sanitize_html(value):
    value = urllib.parse.quote(value)

    value = str.replace(value, "/", "%2F")

    value = BeautifulSoup(value)

    return value.renderContents()


def get_items_for_location(db, location):
    cur = db.cursor()

    sql = """
    SELECT DISTINCT items.wrinNo
    FROM count, items, locations
    WHERE locations.description = (?) AND locations.locID = count.locID AND count.wrinNo = items.wrinNo
    ORDER BY items.name
    """

    cur.execute(sql, (location, ))

    result = cur.fetchall()

    wrinNos = []

    for num in result:
        wrinNos.append(num[0])

    return wrinNos


def add_form_data_to_database(area, formData, db):
    curr = db.cursor()

    sql = """
    SELECT locID
    FROM locations
    WHERE description = (?)
    """

    locIDQuery = curr.execute(sql, (area,))

    locID = ((locIDQuery.fetchone()[0]))

    countList = convert_formData_into_list(formData)

    for item in countList:
        wrinNo = item[0]
        count = item[2]
        if count == 0:
            count = -1
        countType = item[1]
        if (countType == "looseCount"):
            sql = """
                UPDATE count
                SET looseCount = ?, wrinNo = ?
                WHERE locID = ? AND wrinNo = ?;
                """
            curr.execute(sql, (count, wrinNo, locID, wrinNo))
            db.commit()
        if (countType == "sleeveCount"):
            sql = """
                UPDATE count
                SET sleeveCount = ?, wrinNo = ?
                WHERE locID = ? AND wrinNo = ?;
                """
            curr.execute(sql, (count, wrinNo, locID, wrinNo))
            db.commit()
        if (countType == "caseCount"):
            sql = """
                UPDATE count
                SET caseCount = ?, wrinNo = ?
                WHERE locID = ? AND wrinNo = ?;
                """
            curr.execute(sql, (count, wrinNo, locID, wrinNo))
            db.commit()


def convert_formData_into_list(formData):
    dataString = str.split(formData.decode("utf-8"), "&")

    dataSplit = []

    for string in dataString:
        if (string):
            dataSplit.append(str.split(string, "+"))

    miniList = []

    for list in dataSplit:
        for string in list:
            if ("=" in string):
                i = (str.split(string, "="))
                wrinNo = list[0]
                countType = i[0]
                countAmount = i[1]
                if countAmount == "":
                    countAmount = -1
                j = [wrinNo, countType, countAmount]
                miniList.append(j)

    return miniList


def item_data_from_wrinNo(db, wrinNo, locID):
    cur = db.cursor()

    sql = """
    SELECT DISTINCT items.name, items.wrinNo, items.uom, items.caseUnits, items.sleeveUnits
    FROM items
    WHERE wrinNo = (?)
    """

    cur.execute(sql, (wrinNo, ))

    data = cur.fetchone()

    dict = {}

    dict['name'] = data[0]
    dict['wrinNo'] = data[1]
    dict['uom'] = data[2]
    dict['caseUnits'] = data[3]
    dict['sleeveUnits'] = data[4]

    sql = """SELECT locID
    FROM locations
    WHERE description = (?);
    """

    cur.execute(sql, (locID, ))

    result = cur.fetchone()

    area = result[0]

    sql = """SELECT count.caseCount, count.sleeveCount, count.looseCount
    FROM count
    WHERE count.wrinNo = (?) and count.locID = (?);"""

    cur.execute(sql, (wrinNo, area))

    data = cur.fetchone()

    dict['caseCount'] = data[0]
    dict['sleeveCount'] = data[1]
    dict['looseCount'] = data[2]

    if dict['caseCount'] == -1:
        dict['caseCount'] = ""
    if dict['sleeveCount'] == -1:
        dict['sleeveCount'] = ""
    if dict['looseCount'] == -1:
        dict['looseCount'] = ""

    return dict


def get_wrinNo_list(db):
    cur = db.cursor()

    sql = """
    SELECT wrinNo
    FROM items;
    """

    cur.execute(sql)

    wrinNoQuery = cur.fetchall()

    wrinNoList = []

    for result in wrinNoQuery:
        wrinNoList.append(result[0])

    return wrinNoList


def search_count_for_matches(db, wrinNo):
    cur = db.cursor()

    sql = """
        SELECT countID
        FROM count
        WHERE wrinNo = (?)
        """

    cur.execute(sql, (wrinNo, ))

    resultsQuery = cur.fetchall()

    results = []

    for result in resultsQuery:
        results.append(result[0])

    return results


def start_xml(dateTime, session):

    date = dateTime.strftime("%d/%m/%Y")

    currentTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    xml = """<inventoryImport timestamp="%s" counttime="%s" id="%s">
    <items>""" % (date, currentTime, session)

    return xml


def end_xml(xml):
    xml = xml + """
    </items>
</inventoryImport>"""

    return xml


def add_item_to_xml(xml, wrinNo, conn):
    cur = conn.cursor()

    locationList = search_count_for_matches(conn, wrinNo)

    sql = """
        SELECT caseUnits, sleeveUnits
        FROM items
        WHERE wrinNo = (?)
        """

    cur.execute(sql, (wrinNo, ))
    queryResult = cur.fetchall()

    caseUnits = queryResult[0][0]
    sleeveUnits = queryResult[0][1]
    looseUnits = 1

    sql = """
    SELECT locID, caseCount, sleeveCount, looseCount
    FROM count
    WHERE countID = (?)
    """

    result = []

    totalCount = float(0)

    for id in locationList:
        cur.execute(sql, (id, ))
        queryResult = cur.fetchall()
        result.append(queryResult)

    doNotInclude = True


    for i in range(len(result)):
        caseCount = (result[i][0][1])
        sleeveCount = (result[i][0][2])
        looseCount = (result[i][0][3])
        if looseCount != -1:
            totalCount = totalCount + (looseCount * looseUnits)
            doNotInclude = False
        if sleeveCount != -1:
            totalCount = totalCount + (sleeveCount * sleeveUnits)
            doNotInclude = False
        if caseCount != -1:
            totalCount = totalCount + (caseCount * caseUnits)
            doNotInclude = False

    if doNotInclude == False:
        xml = xml + """
            <item id="%s" count="%.2f">""" % (wrinNo, totalCount)

        for i in range(len(result)):
            caseCount = result[i][0][1]
            sleeveCount = result[i][0][2]
            looseCount = result[i][0][3]
            locID = result[i][0][0]
            if looseCount == -1:
                looseCount = 0
            else:
                looseCount = looseCount * looseUnits
            if sleeveCount == -1:
                sleeveCount = 0
            else:
                sleeveCount = sleeveCount * sleeveUnits
            if caseCount == -1:
                caseCount = 0
            else:
                caseCount = caseCount * caseUnits
            xml = xml +"""
                <locationCount locid="%d" caseCount="%.2f" sleeveCount="%.2f" looseCount="%.2f"/>""" % (locID, caseCount, sleeveCount, looseCount)

        xml = xml + """
            </item>"""

    return(xml)


if __name__ == "__main__":

    conn = sqlite3.connect('stocktake.db')

    '''create_db(conn)

    add_locations_to_database(conn)

    add_items_to_database(conn)

    wrin = get_wrinNo_list(conn)

    xml = start_xml()

    xml = add_item_to_xml(xml, 421)

    xml = end_xml(xml)

    print(xml)'''

    open_sessions_data()

