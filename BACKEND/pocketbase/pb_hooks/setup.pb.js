/// <reference path="../pb_data/types.d.ts" />

// Initial data seeding and setup hooks

onAfterBootstrap((e) => {
  console.log("PocketBase started - PlayRight NIL platform ready!")
  console.log("Visit http://localhost:8090/_ to set up admin account")
  console.log("Collections will be created automatically from migrations")
})

function seedSampleData() {
  try {
    // Check if we already have sample data
    const existingAthletes = $app.dao().findCollectionByNameOrId("athletes")
    if (!existingAthletes) {
      console.log("Collections not found yet - will seed after migrations")
      return
    }
    
    const athleteCount = $app.dao().findRecordsByExpr("athletes").length
    if (athleteCount > 0) {
      console.log("Sample data already exists")
      return
    }
    
    console.log("Creating sample data...")
    
    // Create sample athletes
    createSampleAthletes()
    createSampleBrands()
    createSampleDeals()
    
    console.log("Sample data created successfully")
    
  } catch (e) {
    console.log("Error seeding sample data:", e.message)
  }
}

function createSampleAthletes() {
  const athletes = [
    {
      email: "marcus.johnson@university.edu",
      password: "athlete123",
      role: "athlete",
      profile: {
        first_name: "Marcus",
        last_name: "Johnson", 
        sport: "basketball",
        position: "Point Guard",
        school: "State University",
        location: "Los Angeles, CA",
        bio: "Senior point guard with strong leadership and court vision. Passionate about community engagement.",
        nil_eligible: true,
        graduation_year: 2025,
        social_media: {
          instagram: "marcusj_hoops",
          tiktok: "marcusj_basketball"
        }
      }
    },
    {
      email: "sarah.williams@college.edu",
      password: "athlete123",
      role: "athlete", 
      profile: {
        first_name: "Sarah",
        last_name: "Williams",
        sport: "soccer",
        position: "Midfielder",
        school: "Tech College",
        location: "Austin, TX",
        bio: "Dynamic midfielder with excellent ball control and game awareness.",
        nil_eligible: true,
        graduation_year: 2024,
        social_media: {
          instagram: "sarah_soccer",
          tiktok: "sarahw_soccer"
        }
      }
    }
  ]
  
  athletes.forEach(athleteData => {
    try {
      // Create user first
      const user = new Record($app.dao().findCollectionByNameOrId("users"))
      user.set("email", athleteData.email)
      user.set("password", athleteData.password)
      user.set("passwordConfirm", athleteData.password)
      user.set("role", athleteData.role)
      user.set("verified", true)
      user.set("profile_completed", true)
      
      $app.dao().saveRecord(user)
      
      // Create athlete profile
      const athlete = new Record($app.dao().findCollectionByNameOrId("athletes"))
      athlete.set("user", user.id)
      Object.keys(athleteData.profile).forEach(key => {
        athlete.set(key, athleteData.profile[key])
      })
      
      $app.dao().saveRecord(athlete)
      
      console.log(`Created athlete: ${athleteData.profile.first_name} ${athleteData.profile.last_name}`)
    } catch (e) {
      console.log(`Error creating athlete ${athleteData.email}:`, e.message)
    }
  })
}

function createSampleBrands() {
  const brands = [
    {
      email: "nike.local@nike.com",
      password: "brand123",
      role: "brand",
      profile: {
        company_name: "Nike Local Store",
        industry: "sports_apparel",
        location: "Los Angeles, CA",
        description: "Premier athletic wear and equipment for serious athletes.",
        budget_min: 5000,
        budget_max: 25000,
        preferred_sports: ["basketball", "soccer"],
        target_demographics: {
          age_groups: {"18-24": 40, "25-34": 35, "35-44": 25},
          gender: {"male": 60, "female": 40}
        },
        verified: true
      }
    },
    {
      email: "fitness.co@example.com", 
      password: "brand123",
      role: "brand",
      profile: {
        company_name: "Local Fitness Co.",
        industry: "fitness",
        location: "Austin, TX",
        description: "Community fitness center focused on athlete development.",
        budget_min: 2000,
        budget_max: 12000,
        preferred_sports: ["tennis", "swimming", "track"],
        verified: true
      }
    }
  ]
  
  brands.forEach(brandData => {
    try {
      // Create user first
      const user = new Record($app.dao().findCollectionByNameOrId("users"))
      user.set("email", brandData.email)
      user.set("password", brandData.password)
      user.set("passwordConfirm", brandData.password)
      user.set("role", brandData.role)
      user.set("verified", true)
      user.set("profile_completed", true)
      
      $app.dao().saveRecord(user)
      
      // Create brand profile
      const brand = new Record($app.dao().findCollectionByNameOrId("brands"))
      brand.set("user", user.id)
      Object.keys(brandData.profile).forEach(key => {
        brand.set(key, brandData.profile[key])
      })
      
      $app.dao().saveRecord(brand)
      
      console.log(`Created brand: ${brandData.profile.company_name}`)
    } catch (e) {
      console.log(`Error creating brand ${brandData.email}:`, e.message)
    }
  })
}

function createSampleDeals() {
  try {
    // Get sample athlete and brand
    const athletes = $app.dao().findRecordsByExpr("athletes", null, "-created", 2)
    const brands = $app.dao().findRecordsByExpr("brands", null, "-created", 2)
    
    if (athletes.length > 0 && brands.length > 0) {
      const deal = new Record($app.dao().findCollectionByNameOrId("deals"))
      deal.set("athlete", athletes[0].id)
      deal.set("brand", brands[0].id)
      deal.set("title", "Basketball Training Content Partnership")
      deal.set("description", "Create basketball training content featuring Nike products")
      deal.set("value", 15000)
      deal.set("status", "active")
      deal.set("contract_type", "endorsement")
      deal.set("ai_match_score", 87.5)
      deal.set("progress", 75)
      
      $app.dao().saveRecord(deal)
      console.log("Sample deal created")
    }
  } catch (e) {
    console.log("Error creating sample deal:", e.message)
  }
}