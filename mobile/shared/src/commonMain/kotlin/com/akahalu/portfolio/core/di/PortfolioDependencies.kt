package com.akahalu.portfolio.core.di

import com.akahalu.portfolio.core.network.ApiClient
import com.akahalu.portfolio.core.network.NetworkConfig
import com.akahalu.portfolio.core.network.createPlatformHttpClient
import com.akahalu.portfolio.data.portfolio.cache.JsonPortfolioCache
import com.akahalu.portfolio.data.portfolio.cache.PortfolioCacheStorage
import com.akahalu.portfolio.data.portfolio.remote.PortfolioRemoteDataSource
import com.akahalu.portfolio.data.portfolio.repository.PortfolioRepositoryImpl
import com.akahalu.portfolio.domain.portfolio.repository.PortfolioRepository
import io.ktor.client.HttpClient

class PortfolioDependencies(
    networkConfig: NetworkConfig,
    cacheStorage: PortfolioCacheStorage,
) {

    val httpClient: HttpClient = createPlatformHttpClient(
        networkConfig,
    )

    val apiClient: ApiClient = ApiClient(
        httpClient = httpClient,
    )

    val portfolioRemoteDataSource =
        PortfolioRemoteDataSource(
            apiClient = apiClient,
        )

    val portfolioCache = JsonPortfolioCache(
        storage = cacheStorage,
    )

    val portfolioRepository: PortfolioRepository =
        PortfolioRepositoryImpl(
            remoteDataSource = portfolioRemoteDataSource,
            cache = portfolioCache,
        )
}