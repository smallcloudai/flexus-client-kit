def integrations_load(whitelist: list[str]) -> dict[str, dict]:
    result = {}
    for name in whitelist:
        if name == "flexus_policy_document":
            from flexus_client_kit.integrations import fi_pdoc
            async def _init_pdoc(rcx):
                return fi_pdoc.IntegrationPdoc(rcx, rcx.persona.ws_root_group_id)
            result[name] = {
                "integr_tools": [fi_pdoc.POLICY_DOCUMENT_TOOL],
                "integr_init": _init_pdoc,
                "integr_setup_handlers": lambda obj, rcx: [rcx.on_tool_call("flexus_policy_document")(obj.called_by_model)],
            }
        elif name == "print_widget":
            from flexus_client_kit.integrations import fi_widget
            async def _init_widget(rcx):
                return None
            result[name] = {
                "integr_tools": [fi_widget.PRINT_WIDGET_TOOL],
                "integr_init": _init_widget,
                "integr_setup_handlers": lambda obj, rcx: [rcx.on_tool_call("print_widget")(fi_widget.handle_print_widget)],
            }
        elif name == "gmail":
            from flexus_client_kit.integrations import fi_gmail
            async def _init_gmail(rcx):
                return fi_gmail.IntegrationGmail(rcx.fclient, rcx)
            result[name] = {
                "integr_tools": [fi_gmail.GMAIL_TOOL],
                "integr_init": _init_gmail,
                "integr_setup_handlers": lambda obj, rcx: [rcx.on_tool_call("gmail")(obj.called_by_model)],
                "integr_provider": "google",
                "integr_scopes": fi_gmail.GMAIL_SCOPES,
            }
        elif name == "google_calendar":
            from flexus_client_kit.integrations import fi_google_calendar
            async def _init_gcal(rcx):
                return fi_google_calendar.IntegrationGoogleCalendar(rcx.fclient, rcx)
            result[name] = {
                "integr_tools": [fi_google_calendar.GOOGLE_CALENDAR_TOOL],
                "integr_init": _init_gcal,
                "integr_setup_handlers": lambda obj, rcx: [rcx.on_tool_call("google_calendar")(obj.called_by_model)],
                "integr_provider": "google",
                "integr_scopes": fi_google_calendar.REQUIRED_SCOPES,
            }
        else:
            raise ValueError(f"Unknown integration {name!r}")
    return result
