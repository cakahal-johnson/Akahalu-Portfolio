package com.akahalu.portfolio.data.portfolio.dto

import kotlinx.serialization.Serializable

@Serializable
data class ProfileDto(
    val first_name: String,
    val middle_name: String? = null,
    val last_name: String,
    val display_name: String,
    val professional_title: String,
    val headline: String,
    val short_bio: String,
    val biography: String,
    val location: String? = null,
    val country: String? = null,
    val timezone: String? = null,
    val primary_email: String,
    val phone: String? = null,
    val website_url: String? = null,
    val resume_url: String? = null,
    val profile_image_url: String? = null,
    val years_of_experience: Int = 0,
    val availability_status: String = "open_to_opportunities",
    val availability_message: String? = null,
    val is_public: Boolean = false,
    val seo_title: String? = null,
    val seo_description: String? = null,
)
