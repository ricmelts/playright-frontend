/// <reference path="../pb_data/types.d.ts" />

// Auto-calculate AI match score when deal is created
onRecordBeforeCreateRequest((e) => {
  const collection = e.httpContext.get("collection")
  
  if (collection.name !== "deals") {
    return
  }

  // Set initial progress and calculate AI match score
  e.record.set("progress", 0)
  
  const athleteId = e.record.get("athlete")
  const brandId = e.record.get("brand")
  
  if (athleteId && brandId) {
    // Calculate AI match score (simplified version - would call ML service)
    const matchScore = calculateMatchScore(athleteId, brandId)
    e.record.set("ai_match_score", matchScore)
  }

  // Set default status if not provided
  if (!e.record.get("status")) {
    e.record.set("status", "proposed")
  }
}, "deals")

// Update progress based on status changes
onRecordAfterUpdateRequest((e) => {
  const collection = e.httpContext.get("collection")
  
  if (collection.name !== "deals") {
    return
  }

  const oldStatus = e.record.originalCopy().get("status")
  const newStatus = e.record.get("status")
  
  if (oldStatus !== newStatus) {
    let progress = e.record.get("progress") || 0
    
    // Auto-update progress based on status
    switch (newStatus) {
      case "proposed":
        progress = 10
        break
      case "under_review":
        progress = 25
        break
      case "negotiating":
        progress = 50
        break
      case "pending_signatures":
        progress = 75
        break
      case "active":
        progress = 100
        break
      case "completed":
        progress = 100
        break
      case "cancelled":
      case "expired":
        progress = 0
        break
    }
    
    e.record.set("progress", progress)
    $app.dao().saveRecord(e.record)
    
    // Send notifications to relevant parties
    sendDealStatusNotification(e.record, oldStatus, newStatus)
  }
}, "deals")

// Helper function to calculate AI match score
function calculateMatchScore(athleteId, brandId) {
  try {
    const athlete = $app.dao().findRecordById("athletes", athleteId)
    const brand = $app.dao().findRecordById("brands", brandId)
    
    let score = 50 // Base score
    
    // Sport alignment
    const athleteSport = athlete.get("sport")
    const brandSports = brand.get("preferred_sports") || []
    if (brandSports.includes(athleteSport)) {
      score += 20
    }
    
    // Location proximity (simplified)
    const athleteLocation = athlete.get("location")
    const brandLocation = brand.get("location")
    if (athleteLocation === brandLocation) {
      score += 15
    }
    
    // NIL eligibility
    if (athlete.getBool("nil_eligible")) {
      score += 15
    }
    
    return Math.min(score, 100)
  } catch (error) {
    console.log("Error calculating match score:", error)
    return 50 // Default score
  }
}

// Helper function to send notifications
function sendDealStatusNotification(deal, oldStatus, newStatus) {
  // Implementation would integrate with notification service
  console.log(`Deal ${deal.id} status changed from ${oldStatus} to ${newStatus}`)
}