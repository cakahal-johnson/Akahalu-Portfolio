package com.akahalu.portfolio.presentation.contact

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.akahalu.portfolio.domain.portfolio.model.ContactInquiryType
import com.akahalu.portfolio.domain.portfolio.model.Profile
import com.akahalu.portfolio.domain.portfolio.model.ProfileAvailabilityStatus

@Composable
fun ContactScreen(
    uiState: ContactUiState,
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
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp),
        verticalArrangement = Arrangement.Center,
    ) {
        CircularProgressIndicator()
    }
}

@Composable
private fun ContactError(
    message: String,
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp),
        verticalArrangement = Arrangement.Center,
    ) {
        Text(
            text = "Unable to load contact information.",
            style = MaterialTheme.typography.headlineSmall,
        )

        Text(
            text = message,
            modifier = Modifier.padding(top = 8.dp),
            style = MaterialTheme.typography.bodyMedium,
        )
    }
}

@Composable
private fun ContactContent(
    profile: Profile,
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
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(24.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        item {
            Text(
                text = "Contact",
                style = MaterialTheme.typography.headlineLarge,
            )
        }

        item {
            Text(
                text = profile.professionalTitle,
                style = MaterialTheme.typography.titleLarge,
            )
        }

        item {
            Text(
                text = profile.headline,
                style = MaterialTheme.typography.bodyLarge,
            )
        }

        item {
            AvailabilityCard(profile = profile)
        }

        item {
            ContactInformationCard(profile = profile)
        }

        item {
            Text(
                text = "Send a message",
                style = MaterialTheme.typography.headlineSmall,
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
            Text(
                text = "About",
                style = MaterialTheme.typography.titleLarge,
            )
        }

        item {
            Text(
                text = profile.shortBio,
                style = MaterialTheme.typography.bodyLarge,
            )
        }

        item {
            Text(
                text = profile.biography,
                style = MaterialTheme.typography.bodyMedium,
            )
        }

        if (profile.yearsOfExperience > 0) {
            item {
                Text(
                    text = "${profile.yearsOfExperience} years of experience",
                    style = MaterialTheme.typography.titleMedium,
                )
            }
        }

        item {
            ProfileLinksCard(profile = profile)
        }
    }
}

@Composable
private fun AvailabilityCard(
    profile: Profile,
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Text(
                text = "Availability",
                style = MaterialTheme.typography.titleMedium,
            )

            Text(
                text = profile.availabilityStatus.displayName(),
                style = MaterialTheme.typography.bodyLarge,
            )

            profile.availabilityMessage
                ?.takeIf { it.isNotBlank() }
                ?.let { message ->
                    Text(
                        text = message,
                        style = MaterialTheme.typography.bodyMedium,
                    )
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
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Text(
                text = "Contact information",
                style = MaterialTheme.typography.titleMedium,
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
        verticalArrangement = Arrangement.spacedBy(2.dp),
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.labelMedium,
        )

        Text(
            text = value,
            style = MaterialTheme.typography.bodyLarge,
        )
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
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            OutlinedTextField(
                value = form.name,
                onValueChange = onNameChange,
                modifier = Modifier.fillMaxWidth(),
                label = {
                    Text("Name")
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
                singleLine = true,
                enabled = !form.isSubmitting,
            )

            OutlinedTextField(
                value = form.phone,
                onValueChange = onPhoneChange,
                modifier = Modifier.fillMaxWidth(),
                label = {
                    Text("Phone")
                },
                singleLine = true,
                enabled = !form.isSubmitting,
            )

            OutlinedTextField(
                value = form.company,
                onValueChange = onCompanyChange,
                modifier = Modifier.fillMaxWidth(),
                label = {
                    Text("Company")
                },
                singleLine = true,
                enabled = !form.isSubmitting,
            )

            Column {
                TextButton(
                    onClick = {
                        if (!form.isSubmitting) {
                            inquiryMenuExpanded = true
                        }
                    },
                ) {
                    Text(
                        text = "Inquiry type: ${form.inquiryType.displayName}",
                    )
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

            OutlinedTextField(
                value = form.subject,
                onValueChange = onSubjectChange,
                modifier = Modifier.fillMaxWidth(),
                label = {
                    Text("Subject")
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
                minLines = 5,
                enabled = !form.isSubmitting,
            )

            TextButton(
                onClick = {
                    onConsentChange(!form.consentGiven)
                },
                enabled = !form.isSubmitting,
            ) {
                Text(
                    text = if (form.consentGiven) {
                        "[x] I agree to be contacted regarding this inquiry."
                    } else {
                        "[ ] I agree to be contacted regarding this inquiry."
                    },
                )
            }

            form.validationError
                ?.takeIf { it.isNotBlank() }
                ?.let { error ->
                    Text(
                        text = error,
                        color = MaterialTheme.colorScheme.error,
                        style = MaterialTheme.typography.bodyMedium,
                    )
                }

            form.submissionError
                ?.takeIf { it.isNotBlank() }
                ?.let { error ->
                    Text(
                        text = error,
                        color = MaterialTheme.colorScheme.error,
                        style = MaterialTheme.typography.bodyMedium,
                    )
                }

            form.submissionMessage
                ?.takeIf { it.isNotBlank() }
                ?.let { message ->
                    Text(
                        text = message,
                        style = MaterialTheme.typography.bodyMedium,
                    )
                }

            Button(
                onClick = onSubmit,
                modifier = Modifier.fillMaxWidth(),
                enabled = !form.isSubmitting,
            ) {
                if (form.isSubmitting) {
                    CircularProgressIndicator()
                } else {
                    Text("Send message")
                }
            }
        }
    }
}

@Composable
private fun ProfileLinksCard(
    profile: Profile,
) {
    val links = buildList {
        profile.websiteUrl
            ?.takeIf { it.isNotBlank() }
            ?.let { add("Website" to it) }

        profile.resumeUrl
            ?.takeIf { it.isNotBlank() }
            ?.let { add("Resume" to it) }
    }

    if (links.isEmpty()) {
        return
    }

    Card(
        modifier = Modifier.fillMaxWidth(),
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(4.dp),
        ) {
            Text(
                text = "Professional links",
                style = MaterialTheme.typography.titleMedium,
            )

            links.forEach { (label, url) ->
                TextButton(
                    onClick = {
                        // External URL handling remains a separate
                        // platform URL launcher milestone.
                    },
                ) {
                    Text(
                        text = "$label: $url",
                    )
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