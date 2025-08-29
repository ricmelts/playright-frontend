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
    // Send welcome email
    try {
      const userEmail = e.record.get("email")
      const userRole = e.record.get("role")
      const userName = e.record.get("name") || "User"
      
      // Create welcome email content based on user role
      const emailSubject = "Welcome to PlayRight - Your Account is Verified!"
      let emailBody = `
        <html>
          <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
              <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #2563eb;">Welcome to PlayRight!</h1>
              </div>
              
              <p>Hi ${userName},</p>
              
              <p>Congratulations! Your PlayRight account has been successfully verified and you're now ready to start connecting.</p>
              
              ${userRole === 'athlete' ? 
                `<div style="background-color: #f0f9ff; padding: 20px; border-radius: 8px; margin: 20px 0;">
                  <h3 style="color: #1d4ed8; margin-top: 0;">For Athletes:</h3>
                  <ul>
                    <li>Complete your athlete profile with your sports achievements</li>
                    <li>Connect your social media accounts to showcase your following</li>
                    <li>Browse and apply to brand campaigns</li>
                    <li>Build meaningful partnerships with top brands</li>
                  </ul>
                </div>` :
                `<div style="background-color: #f0fdf4; padding: 20px; border-radius: 8px; margin: 20px 0;">
                  <h3 style="color: #16a34a; margin-top: 0;">For Brands:</h3>
                  <ul>
                    <li>Create your brand profile and set your campaign goals</li>
                    <li>Use our AI matching system to find perfect athlete partners</li>
                    <li>Launch targeted campaigns with detailed analytics</li>
                    <li>Track performance and ROI on all partnerships</li>
                  </ul>
                </div>`
              }
              
              <div style="text-align: center; margin: 30px 0;">
                <a href="${$os.getenv("FRONTEND_URL") || "https://playright.ai"}/dashboard" 
                   style="background-color: #2563eb; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; display: inline-block;">
                  Get Started Now
                </a>
              </div>
              
              <p style="margin-top: 30px;">If you have any questions, our support team is here to help. Just reply to this email or contact us through the app.</p>
              
              <p>Best regards,<br>The PlayRight Team</p>
              
              <hr style="margin: 30px 0; border: none; border-top: 1px solid #e5e7eb;">
              <p style="font-size: 12px; color: #6b7280; text-align: center;">
                This email was sent to ${userEmail} because you created an account on PlayRight.
                <br>© 2024 PlayRight. All rights reserved.
              </p>
            </div>
          </body>
        </html>
      `
      
      // Send email using PocketBase's built-in mailer
      const message = new MailerMessage({
        from: {
          address: $os.getenv("SMTP_FROM_EMAIL") || "noreply@playright.ai",
          name: "PlayRight"
        },
        to: [{address: userEmail, name: userName}],
        subject: emailSubject,
        html: emailBody
      })
      
      $app.newMailClient().send(message)
      
      console.log(`Welcome email sent to ${userEmail} (${userRole})`)
      
    } catch (error) {
      console.error(`Failed to send welcome email: ${error}`)
      // Don't throw error to avoid blocking the verification process
    }
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