package com.akahalu.portfolio.domain.portfolio.repository

import com.akahalu.portfolio.domain.portfolio.model.Experience
import com.akahalu.portfolio.domain.portfolio.model.ExperiencePage
import com.akahalu.portfolio.domain.portfolio.model.Profile
import com.akahalu.portfolio.domain.portfolio.model.Project
import com.akahalu.portfolio.domain.portfolio.model.ProjectCategory
import com.akahalu.portfolio.domain.portfolio.model.ProjectPage
import com.akahalu.portfolio.domain.portfolio.model.ProjectTechnology
import com.akahalu.portfolio.domain.portfolio.model.ContactInquirySubmission
import com.akahalu.portfolio.domain.portfolio.model.ContactInquirySubmissionResult

interface PortfolioRepository {

    suspend fun getCategories(): List<ProjectCategory>

    suspend fun getCategory(
        slug: String,
    ): ProjectCategory

    suspend fun getTechnologies(
        category: String? = null,
    ): List<ProjectTechnology>

    suspend fun getTechnology(
        slug: String,
    ): ProjectTechnology

    suspend fun getProjects(
        page: Int = 1,
        pageSize: Int = 20,
        search: String? = null,
        categorySlug: String? = null,
        technologySlug: String? = null,
        isFeatured: Boolean? = null,
    ): ProjectPage

    suspend fun getFeaturedProjects(
        limit: Int = 6,
    ): List<Project>

    suspend fun getProject(
        slug: String,
    ): Project

    suspend fun getExperiences(
        page: Int = 1,
        pageSize: Int = 20,
        search: String? = null,
        employmentType: String? = null,
        locationType: String? = null,
        isCurrent: Boolean? = null,
        isFeatured: Boolean? = null,
    ): ExperiencePage

    suspend fun getFeaturedExperiences(
        limit: Int = 6,
    ): List<Experience>

    suspend fun getExperience(
        slug: String,
    ): Experience

    suspend fun getProfile(): Profile

    suspend fun submitContactInquiry(
        submission: ContactInquirySubmission,
    ): ContactInquirySubmissionResult
}
