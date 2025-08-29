/// <reference path="../pb_data/types.d.ts" />
migrate((db) => {
  const collection = new Collection({
    "id": "campaigns",
    "name": "campaigns",
    "type": "base",
    "system": false,
    "schema": [
      {
        "name": "brand",
        "type": "relation",
        "required": true,
        "options": {
          "collectionId": "brands",
          "cascadeDelete": true,
          "minSelect": null,
          "maxSelect": 1,
          "displayFields": ["company_name"]
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
        "name": "budget",
        "type": "number",
        "required": true,
        "options": {
          "min": 0,
          "max": null
        }
      },
      {
        "name": "target_sports",
        "type": "json",
        "required": true,
        "options": {}
      },
      {
        "name": "target_demographics",
        "type": "json",
        "required": false,
        "options": {}
      },
      {
        "name": "requirements",
        "type": "json",
        "required": false,
        "options": {}
      },
      {
        "name": "start_date",
        "type": "date",
        "required": true,
        "options": {
          "min": "",
          "max": ""
        }
      },
      {
        "name": "end_date",
        "type": "date",
        "required": true,
        "options": {
          "min": "",
          "max": ""
        }
      },
      {
        "name": "application_deadline",
        "type": "date",
        "required": false,
        "options": {
          "min": "",
          "max": ""
        }
      },
      {
        "name": "status",
        "type": "select",
        "required": true,
        "options": {
          "values": ["draft", "active", "paused", "completed", "cancelled"]
        }
      },
      {
        "name": "campaign_type",
        "type": "select",
        "required": true,
        "options": {
          "values": ["social_media", "event_appearance", "product_endorsement", "content_creation", "brand_ambassador", "other"]
        }
      },
      {
        "name": "media_assets",
        "type": "file",
        "required": false,
        "options": {
          "maxSelect": 20,
          "maxSize": 52428800,
          "mimeTypes": ["image/jpeg", "image/png", "image/webp", "video/mp4", "application/pdf"]
        }
      }
    ],
    "indexes": [
      "CREATE INDEX `idx_campaigns_brand` ON `campaigns` (`brand`)",
      "CREATE INDEX `idx_campaigns_status` ON `campaigns` (`status`)",
      "CREATE INDEX `idx_campaigns_budget` ON `campaigns` (`budget`)",
      "CREATE INDEX `idx_campaigns_dates` ON `campaigns` (`start_date`, `end_date`, `application_deadline`)"
    ]
  })

  return Dao(db).saveCollection(collection)
}, (db) => {
  const dao = new Dao(db);
  const collection = dao.findCollectionByNameOrId("campaigns");
  return dao.deleteCollection(collection);
})