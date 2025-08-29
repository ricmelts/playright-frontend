/// <reference path="../pb_data/types.d.ts" />
migrate((db) => {
  const collection = new Collection({
    "id": "brands",
    "name": "brands",
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
        "name": "company_name",
        "type": "text",
        "required": true,
        "options": {
          "min": null,
          "max": 200,
          "pattern": ""
        }
      },
      {
        "name": "industry",
        "type": "select",
        "required": true,
        "options": {
          "values": ["sports_apparel", "fitness", "nutrition", "technology", "automotive", "food_beverage", "retail", "financial", "other"]
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
        "name": "description",
        "type": "text",
        "required": false,
        "options": {
          "min": null,
          "max": 1000,
          "pattern": ""
        }
      },
      {
        "name": "logo",
        "type": "file",
        "required": false,
        "options": {
          "maxSelect": 1,
          "maxSize": 5242880,
          "mimeTypes": ["image/jpeg", "image/png", "image/webp", "image/svg+xml"],
          "thumbs": ["100x100", "300x300"]
        }
      },
      {
        "name": "website",
        "type": "url",
        "required": false,
        "options": {
          "exceptDomains": null,
          "onlyDomains": null
        }
      },
      {
        "name": "target_demographics",
        "type": "json",
        "required": false,
        "options": {}
      },
      {
        "name": "budget_min",
        "type": "number",
        "required": false,
        "options": {
          "min": 0,
          "max": null
        }
      },
      {
        "name": "budget_max",
        "type": "number",
        "required": false,
        "options": {
          "min": 0,
          "max": null
        }
      },
      {
        "name": "preferred_sports",
        "type": "json",
        "required": false,
        "options": {}
      },
      {
        "name": "verified",
        "type": "bool",
        "required": false
      }
    ],
    "indexes": [
      "CREATE INDEX `idx_brands_industry` ON `brands` (`industry`)",
      "CREATE INDEX `idx_brands_verified` ON `brands` (`verified`)",
      "CREATE INDEX `idx_brands_budget` ON `brands` (`budget_min`, `budget_max`)"
    ]
  })

  return Dao(db).saveCollection(collection)
}, (db) => {
  const dao = new Dao(db);
  const collection = dao.findCollectionByNameOrId("brands");
  return dao.deleteCollection(collection);
})