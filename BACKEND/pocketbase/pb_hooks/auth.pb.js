/// <reference path="../pb_data/types.d.ts" />

// Auto-assign user role based on registration context
onRecordAfterCreateRequest((e) => {
  const collection = e.httpContext.get("collection")
  
  if (collection.name !== "users") {
    return
  }

  // Set default role if not provided
  if (!e.record.get("role")) {
    e.record.set("role", "athlete") // Default to athlete
  }

  // Mark profile as incomplete initially
  e.record.set("profile_completed", false)
  e.record.set("verified", false)

  $app.dao().saveRecord(e.record)
}, "users")

// Send welcome email after user verification
onRecordAfterUpdateRequest((e) => {
  const collection = e.httpContext.get("collection")
  
  if (collection.name !== "users") {
    return
  }

  // Check if user was just verified
  const oldVerified = e.record.originalCopy().getBool("verified")
  const newVerified = e.record.getBool("verified")
  
  if (!oldVerified && newVerified) {
    // Send welcome email (implement with your email service)
    console.log(`User ${e.record.get("email")} has been verified - send welcome email`)
  }
}, "users")

// Validate role-specific data requirements
onRecordBeforeUpdateRequest((e) => {
  const collection = e.httpContext.get("collection")
  
  if (collection.name !== "users") {
    return
  }

  const role = e.record.get("role")
  const profileCompleted = e.record.getBool("profile_completed")

  // If marking profile as completed, validate required data exists
  if (profileCompleted && !e.record.originalCopy().getBool("profile_completed")) {
    if (role === "athlete") {
      // Check if athlete profile exists
      const athlete = $app.dao().findFirstRecordByData("athletes", "user", e.record.id)
      if (!athlete) {
        throw new BadRequestError("Athlete profile must be completed before marking as complete")
      }
    } else if (role === "brand") {
      // Check if brand profile exists
      const brand = $app.dao().findFirstRecordByData("brands", "user", e.record.id)
      if (!brand) {
        throw new BadRequestError("Brand profile must be completed before marking as complete")
      }
    }
  }
}, "users")