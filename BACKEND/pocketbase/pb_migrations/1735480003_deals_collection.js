/// <reference path="../pb_data/types.d.ts" />
migrate((db) => {
  const collection = new Collection({
    "id": "deals",
    "name": "deals",
    "type": "base",
    "system": false,
    "schema": [
      {
        "name": "athlete",
        "type": "relation",
        "required": true,
        "options": {
          "collectionId": "athletes",
          "cascadeDelete": false,
          "minSelect": null,
          "maxSelect": 1,
          "displayFields": ["first_name", "last_name"]
        }
      },
      {
        "name": "brand",
        "type": "relation",
        "required": true,
        "options": {
          "collectionId": "brands",
          "cascadeDelete": false,
          "minSelect": null,
          "maxSelect": 1,
          "displayFields": ["company_name"]
        }
      },
      {
        "name": "agent",
        "type": "relation",
        "required": false,
        "options": {
          "collectionId": "_pb_users_auth_",
          "cascadeDelete": false,
          "minSelect": null,
          "maxSelect": 1,
          "displayFields": ["email"]
        }
      },
      {
        "name": "title",
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
          "max": 2000,
          "pattern": ""
        }
      },
      {
        "name": "value",
        "type": "number",
        "required": true,
        "options": {
          "min": 0,
          "max": null
        }
      },
      {
        "name": "status",
        "type": "select",
        "required": true,
        "options": {
          "values": ["proposed", "under_review", "negotiating", "pending_signatures", "active", "completed", "cancelled", "expired"]
        }
      },
      {
        "name": "contract_type",
        "type": "select",
        "required": true,
        "options": {
          "values": ["endorsement", "sponsorship", "appearance", "social_media", "licensing", "other"]
        }
      },
      {
        "name": "start_date",
        "type": "date",
        "required": false,
        "options": {
          "min": "",
          "max": ""
        }
      },
      {
        "name": "end_date",
        "type": "date",
        "required": false,
        "options": {
          "min": "",
          "max": ""
        }
      },
      {
        "name": "deadline",
        "type": "date",
        "required": false,
        "options": {
          "min": "",
          "max": ""
        }
      },
      {
        "name": "terms",
        "type": "json",
        "required": false,
        "options": {}
      },
      {
        "name": "deliverables",
        "type": "json",
        "required": false,
        "options": {}
      },
      {
        "name": "contract_documents",
        "type": "file",
        "required": false,
        "options": {
          "maxSelect": 10,
          "maxSize": 10485760,
          "mimeTypes": ["application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
        }
      },
      {
        "name": "ai_match_score",
        "type": "number",
        "required": false,
        "options": {
          "min": 0,
          "max": 100
        }
      },
      {
        "name": "progress",
        "type": "number",
        "required": false,
        "options": {
          "min": 0,
          "max": 100
        }
      }
    ],
    "indexes": [
      "CREATE INDEX `idx_deals_status` ON `deals` (`status`)",
      "CREATE INDEX `idx_deals_athlete` ON `deals` (`athlete`)",
      "CREATE INDEX `idx_deals_brand` ON `deals` (`brand`)",
      "CREATE INDEX `idx_deals_dates` ON `deals` (`start_date`, `end_date`)",
      "CREATE INDEX `idx_deals_value` ON `deals` (`value`)",
      "CREATE INDEX `idx_deals_match_score` ON `deals` (`ai_match_score`)"
    ]
  })

  return Dao(db).saveCollection(collection)
}, (db) => {
  const dao = new Dao(db);
  const collection = dao.findCollectionByNameOrId("deals");
  return dao.deleteCollection(collection);
})