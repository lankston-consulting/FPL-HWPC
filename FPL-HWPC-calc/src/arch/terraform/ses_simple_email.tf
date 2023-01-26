resource "aws_ses_domain_dkim" "claire_lankstonconsulting_com" {
  domain = "claire@lankstonconsulting.com"
}

resource "aws_ses_domain_dkim" "clairespain_outlook_com" {
  domain = "clairespain@outlook.com"
}

resource "aws_ses_domain_dkim" "colton_lankstonconsulting_com" {
  domain = "colton@lankstonconsulting.com"
}

resource "aws_ses_domain_dkim" "contact_lankstonconsulting_com" {
  domain = "contact@lankstonconsulting.com"
}

resource "aws_ses_domain_dkim" "dan_loeffler_mso_umt_edu" {
  domain = "dan.loeffler@mso.umt.edu"
}

resource "aws_ses_domain_dkim" "dan_loeffler_umt_edu" {
  domain = "dan.loeffler@umt.edu"
}

resource "aws_ses_domain_dkim" "david_l_nicholls_usda_gov" {
  domain = "david.l.nicholls@usda.gov"
}

resource "aws_ses_domain_dkim" "hwpcarbon_com" {
  domain = "hwpcarbon.com"
}

resource "aws_ses_domain_dkim" "keith_stockmann_usda_gov" {
  domain = "keith.stockmann@usda.gov"
}

resource "aws_ses_domain_dkim" "lauren_onofrio_usda_gov" {
  domain = "lauren.onofrio@usda.gov"
}

resource "aws_ses_domain_dkim" "marc_valencia_usda_gov" {
  domain = "marc.valencia@usda.gov"
}

resource "aws_ses_domain_dkim" "nadia_tase_fire_ca_gov" {
  domain = "nadia.tase@fire.ca.gov"
}

resource "aws_ses_domain_dkim" "neprakash_gmail_com" {
  domain = "neprakash@gmail.com"
}

resource "aws_ses_domain_dkim" "poonam_khatri_usda_gov" {
  domain = "Poonam.Khatri@usda.gov"
}

resource "aws_ses_domain_dkim" "prakash_nepal_usda_gov" {
  domain = "prakash.nepal@usda.gov"
}

resource "aws_ses_domain_dkim" "richard_d_bergman_usda_gov" {
  domain = "richard.d.bergman@usda.gov"
}

resource "aws_ses_domain_dkim" "robb_lankstonconsulting_com" {
  domain = "robb@lankstonconsulting.com"
}

resource "aws_ses_domain_identity" "claire_lankstonconsulting_com" {
  domain = "claire@lankstonconsulting.com"
}

resource "aws_ses_domain_identity" "clairespain_outlook_com" {
  domain = "clairespain@outlook.com"
}

resource "aws_ses_domain_identity" "colton_lankstonconsulting_com" {
  domain = "colton@lankstonconsulting.com"
}

resource "aws_ses_domain_identity" "contact_lankstonconsulting_com" {
  domain = "contact@lankstonconsulting.com"
}

resource "aws_ses_domain_identity" "dan_loeffler_mso_umt_edu" {
  domain = "dan.loeffler@mso.umt.edu"
}

resource "aws_ses_domain_identity" "dan_loeffler_umt_edu" {
  domain = "dan.loeffler@umt.edu"
}

resource "aws_ses_domain_identity" "david_l_nicholls_usda_gov" {
  domain = "david.l.nicholls@usda.gov"
}

resource "aws_ses_domain_identity" "hwpcarbon_com" {
  domain = "hwpcarbon.com"
}

resource "aws_ses_domain_identity" "keith_stockmann_usda_gov" {
  domain = "keith.stockmann@usda.gov"
}

resource "aws_ses_domain_identity" "lauren_onofrio_usda_gov" {
  domain = "lauren.onofrio@usda.gov"
}

resource "aws_ses_domain_identity" "marc_valencia_usda_gov" {
  domain = "marc.valencia@usda.gov"
}

resource "aws_ses_domain_identity" "nadia_tase_fire_ca_gov" {
  domain = "nadia.tase@fire.ca.gov"
}

resource "aws_ses_domain_identity" "neprakash_gmail_com" {
  domain = "neprakash@gmail.com"
}

resource "aws_ses_domain_identity" "poonam_khatri_usda_gov" {
  domain = "Poonam.Khatri@usda.gov"
}

resource "aws_ses_domain_identity" "prakash_nepal_usda_gov" {
  domain = "prakash.nepal@usda.gov"
}

resource "aws_ses_domain_identity" "richard_d_bergman_usda_gov" {
  domain = "richard.d.bergman@usda.gov"
}

resource "aws_ses_domain_identity" "robb_lankstonconsulting_com" {
  domain = "robb@lankstonconsulting.com"
}

resource "aws_ses_domain_mail_from" "claire_lankstonconsulting_com" {
  behavior_on_mx_failure = "UseDefaultValue"
  domain                 = "claire@lankstonconsulting.com"
  mail_from_domain       = ""
}

resource "aws_ses_domain_mail_from" "clairespain_outlook_com" {
  behavior_on_mx_failure = "UseDefaultValue"
  domain                 = "clairespain@outlook.com"
  mail_from_domain       = ""
}

resource "aws_ses_domain_mail_from" "colton_lankstonconsulting_com" {
  behavior_on_mx_failure = "UseDefaultValue"
  domain                 = "colton@lankstonconsulting.com"
  mail_from_domain       = ""
}

resource "aws_ses_domain_mail_from" "contact_lankstonconsulting_com" {
  behavior_on_mx_failure = "UseDefaultValue"
  domain                 = "contact@lankstonconsulting.com"
  mail_from_domain       = ""
}

resource "aws_ses_domain_mail_from" "dan_loeffler_mso_umt_edu" {
  behavior_on_mx_failure = "UseDefaultValue"
  domain                 = "dan.loeffler@mso.umt.edu"
  mail_from_domain       = ""
}

resource "aws_ses_domain_mail_from" "dan_loeffler_umt_edu" {
  behavior_on_mx_failure = "UseDefaultValue"
  domain                 = "dan.loeffler@umt.edu"
  mail_from_domain       = ""
}

resource "aws_ses_domain_mail_from" "david_l_nicholls_usda_gov" {
  behavior_on_mx_failure = "UseDefaultValue"
  domain                 = "david.l.nicholls@usda.gov"
  mail_from_domain       = ""
}

resource "aws_ses_domain_mail_from" "hwpcarbon_com" {
  behavior_on_mx_failure = "UseDefaultValue"
  domain                 = "hwpcarbon.com"
  mail_from_domain       = ""
}

resource "aws_ses_domain_mail_from" "keith_stockmann_usda_gov" {
  behavior_on_mx_failure = "UseDefaultValue"
  domain                 = "keith.stockmann@usda.gov"
  mail_from_domain       = ""
}

resource "aws_ses_domain_mail_from" "lauren_onofrio_usda_gov" {
  behavior_on_mx_failure = "UseDefaultValue"
  domain                 = "lauren.onofrio@usda.gov"
  mail_from_domain       = ""
}

resource "aws_ses_domain_mail_from" "marc_valencia_usda_gov" {
  behavior_on_mx_failure = "UseDefaultValue"
  domain                 = "marc.valencia@usda.gov"
  mail_from_domain       = ""
}

resource "aws_ses_domain_mail_from" "nadia_tase_fire_ca_gov" {
  behavior_on_mx_failure = "UseDefaultValue"
  domain                 = "nadia.tase@fire.ca.gov"
  mail_from_domain       = ""
}

resource "aws_ses_domain_mail_from" "neprakash_gmail_com" {
  behavior_on_mx_failure = "UseDefaultValue"
  domain                 = "neprakash@gmail.com"
  mail_from_domain       = ""
}

resource "aws_ses_domain_mail_from" "poonam_khatri_usda_gov" {
  behavior_on_mx_failure = "UseDefaultValue"
  domain                 = "Poonam.Khatri@usda.gov"
  mail_from_domain       = ""
}

resource "aws_ses_domain_mail_from" "prakash_nepal_usda_gov" {
  behavior_on_mx_failure = "UseDefaultValue"
  domain                 = "prakash.nepal@usda.gov"
  mail_from_domain       = ""
}

resource "aws_ses_domain_mail_from" "richard_d_bergman_usda_gov" {
  behavior_on_mx_failure = "UseDefaultValue"
  domain                 = "richard.d.bergman@usda.gov"
  mail_from_domain       = ""
}

resource "aws_ses_domain_mail_from" "robb_lankstonconsulting_com" {
  behavior_on_mx_failure = "UseDefaultValue"
  domain                 = "robb@lankstonconsulting.com"
  mail_from_domain       = ""
}

