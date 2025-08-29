/// <reference path="../pb_data/types.d.ts" />
migrate((db) => {
  const collection = new Collection({
    "id": "athletes",
    "name": "athletes",
    "type": "base",
    "system": false,
    "schema": [
      {
        "name": "user",
        "type": "relation",
        "required": true,
        "options": {
          "collectionId": "_pb_users_auth_",
          "cascadeDelete": true,
          "minSelect": null,
          "maxSelect": 1,
          "displayFields": ["email"]
        }
      },
      {
        "name": "first_name",
        "type": "text",
        "required": true,
        "options": {
          "min": null,
          "max": 100,
          "pattern": ""
        }
      },
      {
        "name": "last_name",
        "type": "text",
        "required": true,
        "options": {
          "min": null,
          "max": 100,
          "pattern": ""
        }
      },
      {
        "name": "sport",
        "type": "select",
        "required": true,
        "options": {
          "values": ["basketball", "soccer", "tennis", "swimming", "football", "baseball", "golf", "track", "other"]
        }
      },
      {
        "name": "position",
        "type": "text",
        "required": false,
        "options": {
          "min": null,
          "max": 100,
          "pattern": ""
        }
      },
      {
        "name": "school",
        "type": "text",
        "required": true,
        "options": {
          "min": null,
          "max": 200,
          "pattern": ""
        }
      },
      {
        "name": "location",
        "type": "text",
        "required": true,
        "options": {
          "min": null,
          "max": 200,
          "pattern": ""
        }
      },
      {
        "name": "bio",
        "type": "text",
        "required": false,
        "options": {
          "min": null,
          "max": 1000,
          "pattern": ""
        }
      },
      {
        "name": "profile_image",
        "type": "file",
        "required": false,
        "options": {
          "maxSelect": 1,
          "maxSize": 5242880,
          "mimeTypes": ["image/jpeg", "image/png", "image/webp"],
          "thumbs": ["100x100", "300x300"]
        }
      },
      {
        "name": "social_media",
        "type": "json",
        "required": false,
        "options": {}
      },
      {
        "name": "nil_eligible",
        "type": "bool",
        "required": true
      },
      {
        "name": "graduation_year",
        "type": "number",
        "required": false,
        "options": {
          "min": 2020,
          "max": 2030
        }
      }
    ],
    "indexes": [
      "CREATE INDEX `idx_athletes_sport` ON `athletes` (`sport`)",
      "CREATE INDEX `idx_athletes_school` ON `athletes` (`school`)",
      "CREATE INDEX `idx_athletes_nil_eligible` ON `athletes` (`nil_eligible`)"
    ]
  })

  return Dao(db).saveCollection(collection)
}, (db) => {
  const dao = new Dao(db);
  const collection = dao.findCollectionByNameOrId("athletes");
  return dao.deleteCollection(collection);
})