/// <reference path="../pb_data/types.d.ts" />
migrate((db) => {
  const collection = new Collection({
    "id": "athlete_metrics",
    "name": "athlete_metrics",
    "type": "base",
    "system": false,
    "schema": [
      {
        "name": "athlete",
        "type": "relation",
        "required": true,
        "options": {
          "collectionId": "athletes",
          "cascadeDelete": true,
          "minSelect": null,
          "maxSelect": 1,
          "displayFields": ["first_name", "last_name"]
        }
      },
      {
        "name": "platform",
        "type": "select",
        "required": true,
        "options": {
          "values": ["instagram", "tiktok", "twitter", "youtube", "facebook", "linkedin", "other"]
        }
      },
      {
        "name": "followers",
        "type": "number",
        "required": false,
        "options": {
          "min": 0,
          "max": null
        }
      },
      {
        "name": "engagement_rate",
        "type": "number",
        "required": false,
        "options": {
          "min": 0,
          "max": 100
        }
      },
      {
        "name": "avg_likes",
        "type": "number",
        "required": false,
        "options": {
          "min": 0,
          "max": null
        }
      },
      {
        "name": "avg_comments",
        "type": "number",
        "required": false,
        "options": {
          "min": 0,
          "max": null
        }
      },
      {
        "name": "avg_shares",
        "type": "number",
        "required": false,
        "options": {
          "min": 0,
          "max": null
        }
      },
      {
        "name": "audience_demographics",
        "type": "json",
        "required": false,
        "options": {}
      },
      {
        "name": "content_categories",
        "type": "json",
        "required": false,
        "options": {}
      },
      {
        "name": "last_updated",
        "type": "date",
        "required": false,
        "options": {
          "min": "",
          "max": ""
        }
      }
    ],
    "indexes": [
      "CREATE UNIQUE INDEX `idx_athlete_metrics_unique` ON `athlete_metrics` (`athlete`, `platform`)",
      "CREATE INDEX `idx_athlete_metrics_followers` ON `athlete_metrics` (`followers`)",
      "CREATE INDEX `idx_athlete_metrics_engagement` ON `athlete_metrics` (`engagement_rate`)",
      "CREATE INDEX `idx_athlete_metrics_updated` ON `athlete_metrics` (`last_updated`)"
    ]
  })

  return Dao(db).saveCollection(collection)
}, (db) => {
  const dao = new Dao(db);
  const collection = dao.findCollectionByNameOrId("athlete_metrics");
  return dao.deleteCollection(collection);
})