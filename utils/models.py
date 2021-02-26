from neomodel import (config, StructuredNode, RelationshipTo, RelationshipFrom,
                      DateTimeProperty, DateProperty, StringProperty, BooleanProperty, One, db, StructuredRel,
                      clear_neo4j_database, IntegerProperty, CardinalityViolation)

#config.DATABASE_URL = 'bolt://neo4j:123@localhost:7687'
config.DATABASE_URL = 'bolt://neo4j:test@neo4j:7687'
config.AUTO_INSTALL_LABELS = True


def generate_export():
    res, cols = db.cypher_query('''
          CALL apoc.export.csv.all(null, {stream:true})
          YIELD file, nodes, relationships, properties, data
          RETURN file, nodes, relationships, properties, data
     ''')
    with open('files/db.csv', 'w', encoding='utf-8') as f:
        print(res[0][4], file=f)


def import_from_csv(some_args=None):
    clear_neo4j_database(db)
    db.cypher_query('''
                    load csv with headers from 'http://server:5000/uploads/Brigade.csv' as row
                        create (:Brigade{id: toInteger(row._id), number:row.number})
            ''')

    db.cypher_query('''
                    load csv with headers from 'http://server:5000/uploads/Order.csv' as row
                        create (:Order{id: toInteger(row._id), cost: toInteger(row.cost), is_done:toBoolean(row.is_done), number: row.number})
             ''')

    db.cypher_query('''
                    load csv with headers from 'http://server:5000/uploads/Employee.csv' as row
                        create (:Employee{id: toInteger(row._id), birth_date: row.birth_date, name: row.name, passport:row.passport, position:row.position})
                 ''')

    db.cypher_query('''
                    load csv with headers from 'http://server:5000/uploads/Material.csv' as row
                        create (:Material{id: toInteger(row._id), name: row.name})
                 ''')



    db.cypher_query('''
                    load csv with headers from 'http://server:5000/uploads/_BRIGADE.csv' as row
                        match (st) where st.id = toInteger(row._start)
                        match (end) where end.id = toInteger(row._end)
                        create (st)-[:BRIGADE]->(end)
                 ''')
    db.cypher_query('''
                    load csv with headers from 'http://server:5000/uploads/_ORDER.csv' as row
                        match (st) where st.id = toInteger(row._start)
                        match (end) where end.id = toInteger(row._end)
                        create (st)-[:ORDER]->(end)
                 ''')

    db.cypher_query('''
                        load csv with headers from 'http://server:5000/uploads/_MATERIAL.csv' as row
                            match (st) where st.id = toInteger(row._start)
                            match (end) where end.id = toInteger(row._end)
                            create (st)-[:MATERIAL{count:toInteger(row.count)}]->(end)
                     ''')

    return True


class MaterialStructure(StructuredRel):
    count = IntegerProperty()


class Employee(StructuredNode):
    name = StringProperty()
    birth_date = DateProperty()
    passport = StringProperty(default='')
    position = StringProperty()

    brigade = RelationshipTo('Brigade', 'BRIGADE', cardinality=One)


class Brigade(StructuredNode):
    number = StringProperty()

    employee = RelationshipFrom('Employee', 'BRIGADE')
    order = RelationshipTo('Order', 'ORDER')

    @classmethod
    def get_done_orders(cls):
        brigades = cls.nodes.all()
        done_orders = []
        brigade_numbers = []
        for brigade in brigades:
            num_of_done_orders = len([order for order in brigade.order.all() if order.is_done])
            done_orders.append(num_of_done_orders)
            brigade_numbers.append(brigade.number)

        return brigade_numbers, done_orders


class Order(StructuredNode):
    number = StringProperty()
    cost = IntegerProperty()
    is_done = BooleanProperty()

    brigade = RelationshipFrom('Brigade', 'ORDER', cardinality=One)
    material = RelationshipFrom('Material', 'MATERIAL', model=MaterialStructure)

    @classmethod
    def get_order_by_id(cls, doctor_id):
        query = f'''
                            match (n:{cls.__name__}) where ID(n)={doctor_id} return n
                '''
        results, columns = db.cypher_query(query)
        if results:
            return cls.inflate(results[0][0])
        return None

    @classmethod
    def get_num_of_done_orders(cls):
        orders = cls.nodes.all()
        num_of_done_orders = len([order for order in orders if order.is_done])

        return len(orders) - num_of_done_orders, num_of_done_orders


class Material(StructuredNode):
    name = StringProperty()

    order = RelationshipTo('Order', 'MATERIAL', cardinality=One, model=MaterialStructure)
