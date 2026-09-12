package com.akahalu.portfolio

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Scaffold
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Modifier
import com.akahalu.portfolio.core.di.PortfolioDependencies
import com.akahalu.portfolio.core.designsystem.theme.AkahaluPortfolioTheme
import com.akahalu.portfolio.core.navigation.AppDestination
import com.akahalu.portfolio.core.navigation.AppNavigator
import com.akahalu.portfolio.core.network.NetworkConfig
import com.akahalu.portfolio.core.platform.ExternalUrlLauncher
import com.akahalu.portfolio.domain.portfolio.model.ContactInquiryType
import com.akahalu.portfolio.domain.portfolio.repository.PortfolioRepository
import com.akahalu.portfolio.presentation.contact.ContactScreen
import com.akahalu.portfolio.presentation.contact.ContactUiState
import com.akahalu.portfolio.presentation.contact.ContactViewModel
import com.akahalu.portfolio.presentation.experience.ExperienceScreen
import com.akahalu.portfolio.presentation.experience.ExperienceUiState
import com.akahalu.portfolio.presentation.experience.ExperienceViewModel
import com.akahalu.portfolio.presentation.home.HomeScreen
import com.akahalu.portfolio.presentation.portfolio.PortfolioUiState
import com.akahalu.portfolio.presentation.portfolio.PortfolioViewModel
import com.akahalu.portfolio.presentation.projects.ProjectDetailScreen
import com.akahalu.portfolio.presentation.projects.ProjectDetailViewModel
import com.akahalu.portfolio.presentation.projects.ProjectsScreen
import com.akahalu.portfolio.presentation.shell.AppNavigationBar
import com.akahalu.portfolio.presentation.skills.SkillsScreen
import com.akahalu.portfolio.presentation.skills.SkillsUiState
import com.akahalu.portfolio.presentation.skills.SkillsViewModel
import kotlinx.coroutines.CoroutineScope
import com.akahalu.portfolio.data.portfolio.cache.PortfolioCacheStorage

@Composable
fun App(
    networkConfig: NetworkConfig,
    externalUrlLauncher: ExternalUrlLauncher,
    cacheStorage: PortfolioCacheStorage,
) {
    AkahaluPortfolioTheme {
        val dependencies = remember(
            networkConfig,
            cacheStorage,
        ) {
            PortfolioDependencies(
                networkConfig = networkConfig,
                cacheStorage = cacheStorage,
            )
        }

        DisposableEffect(dependencies) {
            onDispose {
                dependencies.httpClient.close()
            }
        }

        val scope = rememberCoroutineScope()

        val portfolioViewModel = remember(
            dependencies.portfolioRepository,
            scope,
        ) {
            PortfolioViewModel(
                repository = dependencies.portfolioRepository,
                scope = scope,
            )
        }

        val portfolioUiState by portfolioViewModel.uiState.collectAsState()

        LaunchedEffect(portfolioViewModel) {
            portfolioViewModel.loadPortfolio()
        }

        val experienceViewModel = remember(
            dependencies.portfolioRepository,
            scope,
        ) {
            ExperienceViewModel(
                repository = dependencies.portfolioRepository,
                scope = scope,
            )
        }

        val experienceUiState by experienceViewModel.uiState.collectAsState()

        LaunchedEffect(experienceViewModel) {
            experienceViewModel.loadExperiences()
        }

        val skillsViewModel = remember(
            dependencies.portfolioRepository,
            scope,
        ) {
            SkillsViewModel(
                repository = dependencies.portfolioRepository,
                scope = scope,
            )
        }

        val skillsUiState by skillsViewModel.uiState.collectAsState()

        LaunchedEffect(skillsViewModel) {
            skillsViewModel.loadTechnologies()
        }

        val contactViewModel = remember(
            dependencies.portfolioRepository,
            scope,
        ) {
            ContactViewModel(
                repository = dependencies.portfolioRepository,
                scope = scope,
            )
        }

        val contactUiState by contactViewModel.uiState.collectAsState()

        LaunchedEffect(contactViewModel) {
            contactViewModel.loadProfile()
        }

        val navigator = remember {
            AppNavigator()
        }

        val currentDestination by navigator.currentDestination
            .collectAsState()

        AppContent(
            destination = currentDestination,
            portfolioUiState = portfolioUiState,
            portfolioRepository = dependencies.portfolioRepository,
            scope = scope,
            externalUrlLauncher = externalUrlLauncher,
            onTopLevelDestinationSelected = {
                navigator.navigateToTopLevel(it)
            },
            onProjectSelected = { slug ->
                navigator.navigateToProjectDetail(slug)
            },
            onBackFromProjectDetail = {
                navigator.goBack()
            },
            experienceUiState = experienceUiState,
            onExperienceRetry = experienceViewModel::loadExperiences,
            skillsUiState = skillsUiState,
            contactUiState = contactUiState,
            onContactNameChange = contactViewModel::updateName,
            onContactEmailChange = contactViewModel::updateEmail,
            onContactPhoneChange = contactViewModel::updatePhone,
            onContactCompanyChange = contactViewModel::updateCompany,
            onContactInquiryTypeChange = contactViewModel::updateInquiryType,
            onContactSubjectChange = contactViewModel::updateSubject,
            onContactMessageChange = contactViewModel::updateMessage,
            onContactConsentChange = contactViewModel::updateConsentGiven,
            onContactSubmit = contactViewModel::submitContactInquiry,
        )
    }
}

@Composable
private fun AppContent(
    destination: AppDestination,
    portfolioUiState: PortfolioUiState,
    portfolioRepository: PortfolioRepository,
    scope: CoroutineScope,
    externalUrlLauncher: ExternalUrlLauncher,
    onTopLevelDestinationSelected: (AppDestination) -> Unit,
    onProjectSelected: (String) -> Unit,
    onBackFromProjectDetail: () -> Unit,
    experienceUiState: ExperienceUiState,
    onExperienceRetry: () -> Unit,
    skillsUiState: SkillsUiState,
    contactUiState: ContactUiState,
    onContactNameChange: (String) -> Unit,
    onContactEmailChange: (String) -> Unit,
    onContactPhoneChange: (String) -> Unit,
    onContactCompanyChange: (String) -> Unit,
    onContactInquiryTypeChange: (ContactInquiryType) -> Unit,
    onContactSubjectChange: (String) -> Unit,
    onContactMessageChange: (String) -> Unit,
    onContactConsentChange: (Boolean) -> Unit,
    onContactSubmit: () -> Unit,
) {
    val isDetailDestination =
        destination is AppDestination.ProjectDetail

    Scaffold(
        bottomBar = {
            if (!isDetailDestination) {
                AppNavigationBar(
                    currentDestination = destination,
                    onDestinationSelected = onTopLevelDestinationSelected,
                )
            }
        },
    ) { paddingValues ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues),
        ) {
            when (destination) {
                AppDestination.Home -> {
                    HomeScreen(
                        uiState = portfolioUiState,
                        onProjectSelected = onProjectSelected,
                        onViewProjects = {
                            onTopLevelDestinationSelected(
                                AppDestination.Projects,
                            )
                        },
                        onContact = {
                            onTopLevelDestinationSelected(
                                AppDestination.Contact,
                            )
                        },
                    )
                }

                AppDestination.Projects -> {
                    ProjectsScreen(
                        uiState = portfolioUiState,
                        onProjectSelected = onProjectSelected,
                    )
                }

                is AppDestination.ProjectDetail -> {
                    ProjectDetailRoute(
                        slug = destination.slug,
                        repository = portfolioRepository,
                        scope = scope,
                        externalUrlLauncher = externalUrlLauncher,
                        onBack = onBackFromProjectDetail,
                    )
                }

                AppDestination.Experience -> {
                    ExperienceScreen(
                        uiState = experienceUiState,
                        externalUrlLauncher = externalUrlLauncher,
                        onRetry = onExperienceRetry,
                    )
                }

                AppDestination.Skills -> {
                    SkillsScreen(
                        uiState = skillsUiState,
                    )
                }

                AppDestination.Contact -> {
                    ContactScreen(
                        uiState = contactUiState,
                        externalUrlLauncher = externalUrlLauncher,
                        onNameChange = onContactNameChange,
                        onEmailChange = onContactEmailChange,
                        onPhoneChange = onContactPhoneChange,
                        onCompanyChange = onContactCompanyChange,
                        onInquiryTypeChange = onContactInquiryTypeChange,
                        onSubjectChange = onContactSubjectChange,
                        onMessageChange = onContactMessageChange,
                        onConsentChange = onContactConsentChange,
                        onSubmit = onContactSubmit,
                    )
                }
            }
        }
    }
}

@Composable
private fun ProjectDetailRoute(
    slug: String,
    repository: PortfolioRepository,
    scope: CoroutineScope,
    externalUrlLauncher: ExternalUrlLauncher,
    onBack: () -> Unit,
) {
    val viewModel = remember(
        repository,
        scope,
        slug,
    ) {
        ProjectDetailViewModel(
            repository = repository,
            scope = scope,
        )
    }

    val uiState by viewModel.uiState.collectAsState()

    LaunchedEffect(viewModel, slug) {
        viewModel.loadProject(slug)
    }

    ProjectDetailScreen(
        uiState = uiState,
        onBack = onBack,
        externalUrlLauncher = externalUrlLauncher,
    )
}