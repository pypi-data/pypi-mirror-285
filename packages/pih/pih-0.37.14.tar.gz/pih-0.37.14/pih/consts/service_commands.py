from enum import Enum, auto


class ServiceCommands(Enum):
    ping = auto()
    subscribe = auto()
    unsubscribe = auto()
    create_subscribtions = auto()
    stop_service = auto()
    send_event = auto()
    serve_command = auto()
    # Service admin
    on_service_starts = auto()
    on_service_stops = auto()
    update_service_information = auto()
    get_service_information_list = auto()

    # Log
    send_log_message = auto()
    #
    send_message_to_user_or_workstation = auto()
    add_message_to_queue = auto()
    send_delayed_message = auto()
    # Documents
    create_user_document = auto()
    save_time_tracking_report = auto()
    save_xlsx = auto()
    create_barcodes_for_inventory = auto()
    create_barcode_for_polibase_person = auto()
    create_qr_code = auto()
    check_inventory_report = auto()
    get_inventory_report = auto()
    save_inventory_report_item = auto()
    close_inventory_report = auto()
    # Polibase
    get_polibase_person_by_pin = auto()
    get_polibase_persons_by_pin = auto()
    get_polibase_persons_by_card_registry_folder_name = auto()
    get_polibase_persons_by_name = auto()
    get_polibase_person_pin_list_with_old_format_barcode = auto()
    get_polibase_person_registrator_by_pin = auto()
    get_polibase_persons_pin_by_visit_date = auto()
    get_polibase_persons_by_telephone_number = auto()
    get_polibase_person_pin_by_login = auto()
    get_polibase_person_user_login_and_worstation_name_pair_list = auto()
    #
    get_polibase_person_visits_last_id = auto()
    search_polibase_person_visits = auto()
    #
    set_polibase_person_card_folder_name = auto()
    set_polibase_person_email = auto()
    set_barcode_for_polibase_person = auto()
    check_polibase_person_card_registry_folder_name = auto()

    # ActiveDirectory
    check_user_exists_by_login = auto()
    drop_user_cache = auto()
    drop_workstaion_cache = auto()
    get_user_by_full_name = auto()
    get_users_by_name = auto()
    # get_active_users_by_name = auto()
    get_user_by_login = auto()
    get_user_by_telephone_number = auto()
    get_template_users = auto()
    get_containers = auto()
    get_user_list_by_job_position = auto()
    get_user_list_by_group = auto()
    create_user_by_template = auto()
    set_user_telephone_number = auto()
    authenticate = auto()
    set_user_password = auto()
    set_user_status = auto()
    get_printer_list = auto()
    remove_user = auto()
    get_computer_description_list = auto()
    get_computer_list = auto()
    get_workstation_list_by_user_login = auto()
    get_user_by_workstation = auto()
    # Printer
    printers_report = auto()
    # Orion
    get_free_mark_list = auto()
    get_temporary_mark_list = auto()
    get_mark_person_division_list = auto()
    get_time_tracking = auto()
    get_mark_list = auto()
    get_owner_mark_for_temporary_mark = auto()
    get_mark_by_tab_number = auto()
    get_mark_by_person_name = auto()
    get_free_mark_group_statistics_list = auto()
    get_free_mark_list_by_group_id = auto()
    get_mark_list_by_division_id = auto()
    set_full_name_by_tab_number = auto()
    set_telephone_by_tab_number = auto()
    check_mark_free = auto()
    create_mark = auto()
    remove_mark_by_tab_number = auto()
    make_mark_as_free_by_tab_number = auto()
    make_mark_as_temporary = auto()
    # PolibaseDatabaseBackup
    create_polibase_database_backup = auto()
    # DataStorage::Settings
    set_settings_value = auto()
    get_settings_value = auto()
    # HeatBeat
    heart_beat = auto()
    # Notifier
    register_polibase_person_information_quest = auto()
    search_polibase_person_information_quests = auto()
    update_polibase_person_information_quest = auto()
    # Visit Cached (DS)
    update_polibase_person_visit_to_data_stogare = auto()
    search_polibase_person_visits_in_data_storage = auto()
    # Visit notification
    register_polibase_person_visit_notification = auto()
    search_polibase_person_visit_notifications = auto()
    # Notification confirmation
    search_polibase_person_notification_confirmation = auto()
    update_polibase_person_notification_confirmation = auto()
    #
    check_email_accessibility = auto()
    get_email_information = auto()
    #
    register_delayed_message = auto()
    search_delayed_messages = auto()
    update_delayed_message = auto()
    #
    execute_data_source_query = auto()
    # WORKSTATION
    reboot = auto()
    shutdown = auto()
    log_out = auto()
    # Robocopy::Job
    robocopy_start_job = auto()
    robocopy_get_job_status_list = auto()
    # DataStorage::Storage value
    set_storage_value = auto()
    get_storage_value = auto()
    # Resource Manager
    get_resource_status_list = auto()

    register_ct_indications_value = auto()
    get_last_ct_indications_value_container_list = auto()
    get_last_сhiller_indications_value_container_list = auto()
    #
    test = auto()
    #
    execute_ssh_command = auto()
    get_certificate_information = auto()
    get_unix_free_space_information_by_drive_name = auto()
    print_image = auto()
    #
    get_ogrn_value = auto()
    get_fms_unit_name = auto()
    #
    start_polibase_person_information_quest = auto()
    register_chiller_indications_value = auto()
    #
    add_gkeep_item = auto()
    get_gkeep_item_list_by_any = auto()
    # get_gkeep_item_list_by_name = auto()
    #
    create_note = auto()
    get_note = auto()
    get_note_list_by_label = auto()
    set_polibase_person_telephone_number = auto()
    kill_process = auto()
    #
    register_event = auto()
    get_event = auto()
    remove_event = auto()
    #
    get_polibase_person_operator_by_pin = auto()
    #
    get_barcode_list_information = auto()
    document_type_exists = auto()
    #
    listen_for_new_files = auto()
    #
    recognize_document = auto()
    #
    get_polibase_person_by_email = auto()
    #
    create_statistics_chart = auto()
    #
    execute_polibase_query = auto()
    #
    send_email = auto()
    #
    joke = auto()
    #
    printer_snmp_call = auto()
    #
    update_person_change_date = auto()
    #
    drop_note_cache = auto()
    #
    get_bonus_list = auto()
    #
    door_command = auto()
    #
    mount_facade_for_linux_host = auto()
    #
    get_event_count = auto()
    #
    get_user_list_by_property = auto()