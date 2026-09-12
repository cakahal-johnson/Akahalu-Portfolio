package com.akahalu.portfolio.presentation.contact

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.fadeIn
import androidx.compose.animation.slideInVertically
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Checkbox
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import com.akahalu.portfolio.core.designsystem.tokens.AkahaluSpacing
import com.akahalu.portfolio.core.platform.ExternalUrlLauncher
import com.akahalu.portfolio.domain.portfolio.model.ContactInquiryType
import com.akahalu.portfolio.domain.portfolio.model.Profile
import com.akahalu.portfolio.domain.portfolio.model.ProfileAvailabilityStatus
import com.akahalu.portfolio.presentation.components.SkeletonCard
import com.akahalu.portfolio.presentation.components.SkeletonText

@Composable
fun ContactScreen(
    uiState: ContactUiState,
    externalUrlLauncher: ExternalUrlLauncher,
    onNameChange: (String) -> Unit,
    onEmailChange: (String) -> Unit,
    onPhoneChange: (String) -> Unit,
    onCompanyChange: (String) -> Unit,
    onInquiryTypeChange: (ContactInquiryType) -> Unit,
    onSubjectChange: (String) -> Unit,
    onMessageChange: (String) -> Unit,
    onConsentChange: (Boolean) -> Unit,
    onSubmit: () -> Unit,
) {
    when (uiState) {
        ContactUiState.Loading -> {
            ContactLoading()
        }

        is ContactUiState.Success -> {
            ContactContent(
                profile = uiState.profile,
                form = uiState.form,
                externalUrlLauncher = externalUrlLauncher,
                onNameChange = onNameChange,
                onEmailChange = onEmailChange,
                onPhoneChange = onPhoneChange,
                onCompanyChange = onCompanyChange,
                onInquiryTypeChange = onInquiryTypeChange,
                onSubjectChange = onSubjectChange,
                onMessageChange = onMessageChange,
                onConsentChange = onConsentChange,
                onSubmit = onSubmit,
            )
        }

        is ContactUiState.Error -> {
            ContactError(
                message = uiState.message,
            )
        }
    }
}

@Composable
private fun ContactLoading() {
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(
            AkahaluSpacing.Medium,
        ),
        verticalArrangement = Arrangement.spacedBy(
            AkahaluSpacing.Medium,
        ),
    ) {
        item {
            SkeletonText(
                width = 170.dp,
                height = 34.dp,
            )
        }

        item {
            SkeletonText(
                width = 240.dp,
                height = 20.dp,
            )
        }

        item {
            SkeletonText(
                width = null,
                height = 16.dp,
            )
        }

        item {
            SkeletonCard()
        }

        item {
            SkeletonCard()
        }

        item {
            SkeletonCard()
        }
    }
}

@Composable
private fun ContactError(
    message: String,
) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .padding(AkahaluSpacing.Large),
        contentAlignment = Alignment.Center,
    ) {
        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = MaterialTheme.shapes.large,
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.errorContainer,
            ),
        ) {
            Column(
                modifier = Modifier.padding(
                    AkahaluSpacing.Large,
                ),
                verticalArrangement = Arrangement.spacedBy(
                    AkahaluSpacing.Small,
                ),
            ) {
                Text(
                    text = "Unable to load contact information",
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.SemiBold,
                    color = MaterialTheme.colorScheme.onErrorContainer,
                )

                Text(
                    text = message,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onErrorContainer,
                )
            }
        }
    }
}

@Composable
private fun ContactContent(
    profile: Profile,
    form: ContactFormState,
    externalUrlLauncher: ExternalUrlLauncher,
    onNameChange: (String) -> Unit,
    onEmailChange: (String) -> Unit,
    onPhoneChange: (String) -> Unit,
    onCompanyChange: (String) -> Unit,
    onInquiryTypeChange: (ContactInquiryType) -> Unit,
    onSubjectChange: (String) -> Unit,
    onMessageChange: (String) -> Unit,
    onConsentChange: (Boolean) -> Unit,
    onSubmit: () -> Unit,
) {
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(
            horizontal = AkahaluSpacing.Medium,
            vertical = AkahaluSpacing.Large,
        ),
        verticalArrangement = Arrangement.spacedBy(
            AkahaluSpacing.Medium,
        ),
    ) {
        item {
            ContactHero(
                profile = profile,
            )
        }

        item {
            ContactStats(
                profile = profile,
            )
        }

        item {
            AvailabilityCard(
                profile = profile,
            )
        }

        item {
            ContactInformationCard(
                profile = profile,
            )
        }

        item {
            SectionHeader(
                eyebrow = "START A CONVERSATION",
                title = "Tell me about your project",
                description = "Share a few details and I'll get back to you as soon as possible.",
            )
        }

        item {
            ContactFormCard(
                form = form,
                onNameChange = onNameChange,
                onEmailChange = onEmailChange,
                onPhoneChange = onPhoneChange,
                onCompanyChange = onCompanyChange,
                onInquiryTypeChange = onInquiryTypeChange,
                onSubjectChange = onSubjectChange,
                onMessageChange = onMessageChange,
                onConsentChange = onConsentChange,
                onSubmit = onSubmit,
            )
        }

        item {
            AboutCard(
                profile = profile,
            )
        }

        item {
            ProfileLinksCard(
                profile = profile,
                externalUrlLauncher = externalUrlLauncher,
            )
        }

        item {
            Spacer(
                modifier = Modifier.height(
                    AkahaluSpacing.Medium,
                ),
            )
        }
    }
}

@Composable
private fun ContactHero(
    profile: Profile,
) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(
                horizontal = AkahaluSpacing.Small,
            ),
        verticalArrangement = Arrangement.spacedBy(
            AkahaluSpacing.Small,
        ),
    ) {
        Text(
            text = "LET'S CONNECT",
            style = MaterialTheme.typography.labelLarge,
            color = MaterialTheme.colorScheme.primary,
            fontWeight = FontWeight.Bold,
        )

        Text(
            text = "Contact",
            style = MaterialTheme.typography.headlineLarge,
            fontWeight = FontWeight.Bold,
        )

        Text(
            text = profile.professionalTitle,
            style = MaterialTheme.typography.titleLarge,
            fontWeight = FontWeight.SemiBold,
        )

        Text(
            text = profile.headline,
            style = MaterialTheme.typography.bodyLarge,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }
}

@Composable
private fun ContactStats(
    profile: Profile,
) {
    FlowRow(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(
            AkahaluSpacing.Small,
        ),
        verticalArrangement = Arrangement.spacedBy(
            AkahaluSpacing.Small,
        ),
    ) {
        ContactStat(
            value = "${profile.yearsOfExperience}+",
            label = "Years experience",
        )

        ContactStat(
            value = profile.availabilityStatus.shortLabel(),
            label = "Availability",
            compactValue = true,
        )

        profile.location
            ?.takeIf { it.isNotBlank() }
            ?.let { location ->
                ContactStat(
                    value = location,
                    label = "Based in",
                    compactValue = true,
                )
            }
    }
}

@Composable
private fun ContactStat(
    value: String,
    label: String,
    compactValue: Boolean = false,
) {
    Card(
        modifier = Modifier.width(150.dp),
        shape = MaterialTheme.shapes.medium,
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceContainer,
        ),
    ) {
        Column(
            modifier = Modifier.padding(
                AkahaluSpacing.Medium,
            ),
            verticalArrangement = Arrangement.spacedBy(
                AkahaluSpacing.ExtraSmall,
            ),
        ) {
            Text(
                text = value,
                style = if (compactValue) {
                    MaterialTheme.typography.titleMedium
                } else {
                    MaterialTheme.typography.headlineSmall
                },
                fontWeight = FontWeight.Bold,
                maxLines = 2,
            )

            Text(
                text = label,
                style = MaterialTheme.typography.labelMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
    }
}

@Composable
private fun AvailabilityCard(
    profile: Profile,
) {
    val isPositive =
        profile.availabilityStatus != ProfileAvailabilityStatus.UNAVAILABLE

    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = MaterialTheme.shapes.large,
        colors = CardDefaults.cardColors(
            containerColor = if (isPositive) {
                MaterialTheme.colorScheme.primaryContainer
            } else {
                MaterialTheme.colorScheme.surfaceContainer
            },
        ),
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(AkahaluSpacing.Large),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(
                AkahaluSpacing.Medium,
            ),
        ) {
            Box(
                modifier = Modifier
                    .size(12.dp)
                    .clip(CircleShape)
                    .background(
                        color = if (isPositive) {
                            MaterialTheme.colorScheme.primary
                        } else {
                            MaterialTheme.colorScheme.onSurfaceVariant
                        },
                    ),
            )

            Column(
                modifier = Modifier.weight(1f),
                verticalArrangement = Arrangement.spacedBy(
                    AkahaluSpacing.ExtraSmall,
                ),
            ) {
                Text(
                    text = profile.availabilityStatus.displayName(),
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold,
                )

                profile.availabilityMessage
                    ?.takeIf { it.isNotBlank() }
                    ?.let { message ->
                        Text(
                            text = message,
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    }
            }
        }
    }
}

@Composable
private fun ContactInformationCard(
    profile: Profile,
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = MaterialTheme.shapes.large,
    ) {
        Column(
            modifier = Modifier.padding(AkahaluSpacing.Large),
            verticalArrangement = Arrangement.spacedBy(
                AkahaluSpacing.Medium,
            ),
        ) {
            SectionHeader(
                eyebrow = "CONTACT DETAILS",
                title = "Let's make it easy to reach me",
            )

            ContactField(
                label = "Email",
                value = profile.primaryEmail,
            )

            profile.phone
                ?.takeIf { it.isNotBlank() }
                ?.let { phone ->
                    ContactField(
                        label = "Phone",
                        value = phone,
                    )
                }

            val location = listOfNotNull(
                profile.location?.takeIf { it.isNotBlank() },
                profile.country?.takeIf { it.isNotBlank() },
            ).joinToString(", ")

            if (location.isNotBlank()) {
                ContactField(
                    label = "Location",
                    value = location,
                )
            }

            profile.timezone
                ?.takeIf { it.isNotBlank() }
                ?.let { timezone ->
                    ContactField(
                        label = "Timezone",
                        value = timezone,
                    )
                }
        }
    }
}

@Composable
private fun ContactField(
    label: String,
    value: String,
) {
    Column(
        verticalArrangement = Arrangement.spacedBy(
            AkahaluSpacing.ExtraSmall,
        ),
    ) {
        Text(
            text = label.uppercase(),
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.primary,
            fontWeight = FontWeight.Bold,
        )

        Text(
            text = value,
            style = MaterialTheme.typography.bodyLarge,
        )
    }
}

@Composable
private fun SectionHeader(
    eyebrow: String,
    title: String,
    description: String? = null,
) {
    Column(
        modifier = Modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(
            AkahaluSpacing.ExtraSmall,
        ),
    ) {
        Text(
            text = eyebrow,
            style = MaterialTheme.typography.labelMedium,
            color = MaterialTheme.colorScheme.primary,
            fontWeight = FontWeight.Bold,
        )

        Text(
            text = title,
            style = MaterialTheme.typography.headlineSmall,
            fontWeight = FontWeight.Bold,
        )

        description?.let {
            Text(
                text = it,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
    }
}

@Composable
private fun ContactFormCard(
    form: ContactFormState,
    onNameChange: (String) -> Unit,
    onEmailChange: (String) -> Unit,
    onPhoneChange: (String) -> Unit,
    onCompanyChange: (String) -> Unit,
    onInquiryTypeChange: (ContactInquiryType) -> Unit,
    onSubjectChange: (String) -> Unit,
    onMessageChange: (String) -> Unit,
    onConsentChange: (Boolean) -> Unit,
    onSubmit: () -> Unit,
) {
    var inquiryMenuExpanded by remember {
        mutableStateOf(false)
    }

    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = MaterialTheme.shapes.large,
    ) {
        Column(
            modifier = Modifier.padding(AkahaluSpacing.Large),
            verticalArrangement = Arrangement.spacedBy(
                AkahaluSpacing.Medium,
            ),
        ) {
            OutlinedTextField(
                value = form.name,
                onValueChange = onNameChange,
                modifier = Modifier.fillMaxWidth(),
                label = {
                    Text("Name")
                },
                placeholder = {
                    Text("Your full name")
                },
                singleLine = true,
                enabled = !form.isSubmitting,
            )

            OutlinedTextField(
                value = form.email,
                onValueChange = onEmailChange,
                modifier = Modifier.fillMaxWidth(),
                label = {
                    Text("Email")
                },
                placeholder = {
                    Text("you@example.com")
                },
                keyboardOptions = KeyboardOptions(
                    keyboardType = KeyboardType.Email,
                ),
                singleLine = true,
                enabled = !form.isSubmitting,
            )

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(
                    AkahaluSpacing.Small,
                ),
            ) {
                OutlinedTextField(
                    value = form.phone,
                    onValueChange = onPhoneChange,
                    modifier = Modifier.weight(1f),
                    label = {
                        Text("Phone")
                    },
                    singleLine = true,
                    enabled = !form.isSubmitting,
                )

                OutlinedTextField(
                    value = form.company,
                    onValueChange = onCompanyChange,
                    modifier = Modifier.weight(1f),
                    label = {
                        Text("Company")
                    },
                    singleLine = true,
                    enabled = !form.isSubmitting,
                )
            }

            Column(
                verticalArrangement = Arrangement.spacedBy(
                    AkahaluSpacing.ExtraSmall,
                ),
            ) {
                Text(
                    text = "Inquiry type",
                    style = MaterialTheme.typography.labelLarge,
                    fontWeight = FontWeight.SemiBold,
                )

                Box {
                    TextButton(
                        onClick = {
                            if (!form.isSubmitting) {
                                inquiryMenuExpanded = true
                            }
                        },
                        modifier = Modifier.fillMaxWidth(),
                    ) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically,
                        ) {
                            Text(
                                text = form.inquiryType.displayName,
                                style = MaterialTheme.typography.bodyLarge,
                            )

                            Text(
                                text = "▼",
                                style = MaterialTheme.typography.labelMedium,
                                color = MaterialTheme.colorScheme.primary,
                            )
                        }
                    }

                    DropdownMenu(
                        expanded = inquiryMenuExpanded,
                        onDismissRequest = {
                            inquiryMenuExpanded = false
                        },
                    ) {
                        ContactInquiryType.entries.forEach { type ->
                            DropdownMenuItem(
                                text = {
                                    Text(type.displayName)
                                },
                                onClick = {
                                    inquiryMenuExpanded = false
                                    onInquiryTypeChange(type)
                                },
                            )
                        }
                    }
                }
            }

            OutlinedTextField(
                value = form.subject,
                onValueChange = onSubjectChange,
                modifier = Modifier.fillMaxWidth(),
                label = {
                    Text("Subject")
                },
                placeholder = {
                    Text("How can I help?")
                },
                singleLine = true,
                enabled = !form.isSubmitting,
            )

            OutlinedTextField(
                value = form.message,
                onValueChange = onMessageChange,
                modifier = Modifier.fillMaxWidth(),
                label = {
                    Text("Message")
                },
                placeholder = {
                    Text(
                        "Tell me about your project, opportunity or question...",
                    )
                },
                minLines = 6,
                enabled = !form.isSubmitting,
                supportingText = {
                    Text(
                        text = "${form.message.length} characters",
                    )
                },
            )

            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Checkbox(
                    checked = form.consentGiven,
                    onCheckedChange = onConsentChange,
                    enabled = !form.isSubmitting,
                )

                Spacer(
                    modifier = Modifier.width(
                        AkahaluSpacing.Small,
                    ),
                )

                Text(
                    text = "I agree to be contacted regarding this inquiry.",
                    style = MaterialTheme.typography.bodyMedium,
                )
            }

            FormMessage(
                message = form.validationError,
                isError = true,
            )

            FormMessage(
                message = form.submissionError,
                isError = true,
            )

            FormMessage(
                message = form.submissionMessage,
                isError = false,
            )

            Button(
                onClick = onSubmit,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(52.dp),
                enabled = !form.isSubmitting,
                shape = RoundedCornerShape(14.dp),
            ) {
                if (form.isSubmitting) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(20.dp),
                        strokeWidth = 2.dp,
                    )
                } else {
                    Text(
                        text = "Send message",
                        fontWeight = FontWeight.SemiBold,
                    )
                }
            }
        }
    }
}

@Composable
private fun FormMessage(
    message: String?,
    isError: Boolean,
) {
    AnimatedVisibility(
        visible = !message.isNullOrBlank(),
        enter = fadeIn() + slideInVertically(),
    ) {
        Surface(
            modifier = Modifier.fillMaxWidth(),
            shape = MaterialTheme.shapes.medium,
            color = if (isError) {
                MaterialTheme.colorScheme.errorContainer
            } else {
                MaterialTheme.colorScheme.primaryContainer
            },
        ) {
            Text(
                text = message.orEmpty(),
                modifier = Modifier.padding(
                    AkahaluSpacing.Medium,
                ),
                color = if (isError) {
                    MaterialTheme.colorScheme.onErrorContainer
                } else {
                    MaterialTheme.colorScheme.onPrimaryContainer
                },
                style = MaterialTheme.typography.bodyMedium,
            )
        }
    }
}

@Composable
private fun AboutCard(
    profile: Profile,
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = MaterialTheme.shapes.large,
    ) {
        Column(
            modifier = Modifier.padding(AkahaluSpacing.Large),
            verticalArrangement = Arrangement.spacedBy(
                AkahaluSpacing.Medium,
            ),
        ) {
            SectionHeader(
                eyebrow = "ABOUT",
                title = "A little more about me",
            )

            Text(
                text = profile.shortBio,
                style = MaterialTheme.typography.bodyLarge,
            )

            HorizontalDivider()

            Text(
                text = profile.biography,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
    }
}

@Composable
private fun ProfileLinksCard(
    profile: Profile,
    externalUrlLauncher: ExternalUrlLauncher,
) {
    val links = buildList {
        profile.websiteUrl
            ?.takeIf { it.isNotBlank() }
            ?.let {
                add("Website" to it)
            }

        profile.resumeUrl
            ?.takeIf { it.isNotBlank() }
            ?.let {
                add("Resume" to it)
            }
    }

    if (links.isEmpty()) {
        return
    }

    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = MaterialTheme.shapes.large,
    ) {
        Column(
            modifier = Modifier.padding(AkahaluSpacing.Large),
            verticalArrangement = Arrangement.spacedBy(
                AkahaluSpacing.Small,
            ),
        ) {
            SectionHeader(
                eyebrow = "PROFESSIONAL LINKS",
                title = "Explore my work",
            )

            links.forEach { (label, url) ->
                TextButton(
                    onClick = {
                        externalUrlLauncher.openUrl(url)
                    },
                    modifier = Modifier.fillMaxWidth(),
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Text(
                            text = label,
                            fontWeight = FontWeight.SemiBold,
                        )

                        Text(
                            text = "Open →",
                            color = MaterialTheme.colorScheme.primary,
                        )
                    }
                }
            }
        }
    }
}

private fun ProfileAvailabilityStatus.displayName(): String {
    return when (this) {
        ProfileAvailabilityStatus.AVAILABLE ->
            "Available"

        ProfileAvailabilityStatus.OPEN_TO_OPPORTUNITIES ->
            "Open to opportunities"

        ProfileAvailabilityStatus.LIMITED_AVAILABILITY ->
            "Limited availability"

        ProfileAvailabilityStatus.UNAVAILABLE ->
            "Currently unavailable"
    }
}

private fun ProfileAvailabilityStatus.shortLabel(): String {
    return when (this) {
        ProfileAvailabilityStatus.AVAILABLE ->
            "Available"

        ProfileAvailabilityStatus.OPEN_TO_OPPORTUNITIES ->
            "Open"

        ProfileAvailabilityStatus.LIMITED_AVAILABILITY ->
            "Limited"

        ProfileAvailabilityStatus.UNAVAILABLE ->
            "Unavailable"
    }
}