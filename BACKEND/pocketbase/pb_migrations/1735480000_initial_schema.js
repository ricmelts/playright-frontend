/// <reference path="../pb_data/types.d.ts" />
migrate((db) => {
  // Extend default users collection with additional fields
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("users")

  // Add custom fields to existing users collection
  // Add role field
  collection.schema.addField(new SchemaField({
    "name": "role",
    "type": "select", 
    "required": false,
    "options": {
      "values": ["athlete", "brand", "agent", "admin"]
    }
  }))

  // Add profile_completed field (verified already exists)
  collection.schema.addField(new SchemaField({
    "name": "profile_completed",
    "type": "bool",
    "required": false
  }))

  return dao.saveCollection(collection)
}, (db) => {
  // Rollback - remove added fields
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("users")
  
  // Remove custom fields  
  collection.schema.removeField("role")
  collection.schema.removeField("profile_completed")
  
  return dao.saveCollection(collection)
})