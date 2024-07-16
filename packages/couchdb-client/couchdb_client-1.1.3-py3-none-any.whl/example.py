import couchdb_client

db = couchdb_client.CouchDB('admin', 'admin', 'mc')

# create a document instance
doc = db.document({
    'host': 'test',
    'port': 25555
})
doc.create()  # create the document in the database

print(db.get_document(doc.id))  # get the document
# note: doc.id is the same as doc['_id']

# update the document
doc['host'] = 'test2'
doc.update()

# get the document again to the the updated data
print(db.get_document(doc.id))

# delete the document
doc.delete()

print(db.get_document(doc.id))  # should return none since the document was deleted

print(db.get_all_documents(skip=100, limit=10))  # get 10 documents, starting from the 100th
