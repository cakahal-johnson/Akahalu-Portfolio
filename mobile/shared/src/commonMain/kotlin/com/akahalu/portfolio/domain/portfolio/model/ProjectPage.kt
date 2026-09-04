package com.akahalu.portfolio.domain.portfolio.model

data class ProjectPage(
    val items: List<Project>,
    val page: Int,
    val pageSize: Int,
    val totalItems: Int,
    val totalPages: Int,
    val hasNextPage: Boolean,
    val hasPreviousPage: Boolean,
)