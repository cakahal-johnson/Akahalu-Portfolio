package com.akahalu.portfolio.data.portfolio.dto

import kotlinx.serialization.Serializable

@Serializable
data class ExperienceSummaryDto(
    val id: String,
    val company_name: String,
    val job_title: String,
    val slug: String,
    val employment_type: String,
    val location: String? = null,
    val location_type: String,
    val start_date: String,
    val end_date: String? = null,
    val is_current: Boolean,
    val summary: String,
    val company_website: String? = null,
    val company_logo_url: String? = null,
    val sort_order: Int,
    val is_featured: Boolean,
)