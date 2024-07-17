from pih.consts.rpc import RPC
from pih.consts.hosts import Hosts
from pih.consts.service import ServiceRoleBase
from pih.collections.service import ServiceDescription
from pih.consts.service_commands import ServiceCommands
from ipih import SERVICE_ADMIN_HOST_NAME, SERVICE_ADMIN_GRPC_PORT

class ServiceRoles(ServiceRoleBase):

    SERVICE_ADMIN = ServiceDescription(
        "ServiceAdmin",
        host=SERVICE_ADMIN_HOST_NAME,
        port=RPC.PORT(SERVICE_ADMIN_GRPC_PORT),
        commands=(
            ServiceCommands.on_service_starts,
            ServiceCommands.on_service_stops,
            ServiceCommands.get_service_information_list,
            ServiceCommands.heart_beat,
        ),
    )

    EVENT = ServiceDescription(
        "Event",
        commands=(ServiceCommands.send_log_message, ServiceCommands.send_event),
    )

    DS = ServiceDescription(
        "DataSource",
        commands=(
            ServiceCommands.register_polibase_person_information_quest,
            ServiceCommands.search_polibase_person_information_quests,
            ServiceCommands.update_polibase_person_information_quest,
            #
            ServiceCommands.update_polibase_person_visit_to_data_stogare,
            ServiceCommands.search_polibase_person_visits_in_data_storage,
            #
            ServiceCommands.register_polibase_person_visit_notification,
            ServiceCommands.search_polibase_person_visit_notifications,
            #
            ServiceCommands.register_delayed_message,
            ServiceCommands.search_delayed_messages,
            ServiceCommands.update_delayed_message,
            #
            ServiceCommands.get_settings_value,
            ServiceCommands.set_settings_value,
            #
            ServiceCommands.search_polibase_person_notification_confirmation,
            ServiceCommands.update_polibase_person_notification_confirmation,
            #
            ServiceCommands.get_storage_value,
            ServiceCommands.set_storage_value,
            #
            ServiceCommands.get_ogrn_value,
            ServiceCommands.get_fms_unit_name,
            #
            ServiceCommands.register_chiller_indications_value,
            ServiceCommands.register_ct_indications_value,
            ServiceCommands.get_last_ct_indications_value_container_list,
            ServiceCommands.get_last_сhiller_indications_value_container_list,
            #
            ServiceCommands.get_gkeep_item_list_by_any,
            ServiceCommands.add_gkeep_item,
            #
            ServiceCommands.register_event,
            ServiceCommands.get_event,
            ServiceCommands.remove_event,
            #
            ServiceCommands.execute_data_source_query,
            ServiceCommands.joke,
            ServiceCommands.get_event_count,
        ),
    )

    AD = ServiceDescription(
        "ActiveDirectory",
        commands=(
            ServiceCommands.authenticate,
            ServiceCommands.check_user_exists_by_login,
            ServiceCommands.get_user_by_full_name,
            ServiceCommands.get_users_by_name,
            ServiceCommands.get_user_by_login,
            ServiceCommands.get_user_by_telephone_number,
            ServiceCommands.get_template_users,
            ServiceCommands.get_containers,
            ServiceCommands.get_user_list_by_job_position,
            ServiceCommands.get_user_list_by_group,
            ServiceCommands.get_printer_list,
            ServiceCommands.get_computer_list,
            ServiceCommands.get_computer_description_list,
            ServiceCommands.get_workstation_list_by_user_login,
            ServiceCommands.get_user_by_workstation,
            ServiceCommands.create_user_by_template,
            ServiceCommands.set_user_telephone_number,
            ServiceCommands.set_user_password,
            ServiceCommands.set_user_status,
            ServiceCommands.remove_user,
            ServiceCommands.drop_user_cache,
            ServiceCommands.drop_workstaion_cache,
            ServiceCommands.get_user_list_by_property,
        ),
    )

    RECOGNIZE = ServiceDescription(
        "Recognize",
        commands=(
            ServiceCommands.get_barcode_list_information,
            ServiceCommands.document_type_exists,
            ServiceCommands.recognize_document,
        ),
    )

    FILE_WATCHDOG = ServiceDescription(
        "FileWatchdog", commands=(ServiceCommands.listen_for_new_files,)
    )

    """
    FILE_ORGANIZER = ServiceDescription(
        "FileOrganizer",
        description="File organizer service",
        host=HOSTS.WS255.NAME,
    )
    """

    MAIL = ServiceDescription(
        "Mail",
        commands=(
            ServiceCommands.check_email_accessibility,
            ServiceCommands.send_email,
            ServiceCommands.get_email_information,
        ),
    )

    DOCS = ServiceDescription(
        "Docs",
        commands=(
            ServiceCommands.get_inventory_report,
            ServiceCommands.create_user_document,
            ServiceCommands.save_time_tracking_report,
            ServiceCommands.create_barcodes_for_inventory,
            ServiceCommands.create_barcode_for_polibase_person,
            ServiceCommands.create_qr_code,
            ServiceCommands.check_inventory_report,
            ServiceCommands.save_inventory_report_item,
            ServiceCommands.close_inventory_report,
            ServiceCommands.create_note,
            ServiceCommands.get_note,
            ServiceCommands.get_note_list_by_label,
            ServiceCommands.create_statistics_chart,
            ServiceCommands.save_xlsx,
            ServiceCommands.drop_note_cache,
        ),
    )

    MARK = ServiceDescription(
        "Mark",
        commands=(
            ServiceCommands.get_free_mark_list,
            ServiceCommands.get_temporary_mark_list,
            ServiceCommands.get_mark_person_division_list,
            ServiceCommands.get_time_tracking,
            ServiceCommands.get_mark_list,
            ServiceCommands.get_mark_by_tab_number,
            ServiceCommands.get_mark_by_person_name,
            ServiceCommands.get_free_mark_group_statistics_list,
            ServiceCommands.get_free_mark_list_by_group_id,
            ServiceCommands.get_owner_mark_for_temporary_mark,
            ServiceCommands.get_mark_list_by_division_id,
            ServiceCommands.set_full_name_by_tab_number,
            ServiceCommands.set_telephone_by_tab_number,
            ServiceCommands.check_mark_free,
            ServiceCommands.create_mark,
            ServiceCommands.make_mark_as_free_by_tab_number,
            ServiceCommands.make_mark_as_temporary,
            ServiceCommands.remove_mark_by_tab_number,
            ServiceCommands.door_command,
        ),
    )

    POLIBASE = ServiceDescription(
        "Polibase",
        commands=(
            ServiceCommands.get_polibase_person_by_pin,
            ServiceCommands.get_polibase_persons_by_pin,
            ServiceCommands.get_polibase_persons_by_telephone_number,
            ServiceCommands.get_polibase_persons_by_name,
            ServiceCommands.get_polibase_persons_by_card_registry_folder_name,
            ServiceCommands.get_polibase_person_registrator_by_pin,
            ServiceCommands.get_polibase_person_pin_list_with_old_format_barcode,
            #
            ServiceCommands.get_polibase_persons_pin_by_visit_date,
            #
            ServiceCommands.search_polibase_person_visits,
            ServiceCommands.get_polibase_person_visits_last_id,
            #
            ServiceCommands.set_polibase_person_card_folder_name,
            ServiceCommands.set_polibase_person_email,
            ServiceCommands.set_barcode_for_polibase_person,
            ServiceCommands.check_polibase_person_card_registry_folder_name,
            ServiceCommands.set_polibase_person_telephone_number,
            ServiceCommands.get_polibase_person_operator_by_pin,
            ServiceCommands.get_polibase_person_by_email,
            #
            ServiceCommands.execute_polibase_query,
            ServiceCommands.update_person_change_date,
            ServiceCommands.get_polibase_person_pin_by_login,
            ServiceCommands.get_polibase_person_user_login_and_worstation_name_pair_list,
            ServiceCommands.get_bonus_list,
        ),
    )
    
    GATEWAY = ServiceDescription("Gateway")

    MESSAGE_RECEIVER = ServiceDescription("MessageReceiver")

    WEB_SERVER = ServiceDescription("WebServer")

    CHECKER = ServiceDescription(
        "Checker", commands=(ServiceCommands.get_resource_status_list,)
    )

    AUTOMATION = ServiceDescription("Automation")

    MOBILE_HELPER = ServiceDescription("MobileHelper", standalone_name="mio")

    POLIBASE_AUTOMATION = ServiceDescription(
        "PolibaseAutomation", description="Polibase automation service"
    )

    MESSAGE_QUEUE = ServiceDescription(
        "MessageQueue",
        commands=(ServiceCommands.add_message_to_queue,),
    )

    NOTIFICATION_AUTOMATION = ServiceDescription("NotificationAutomation")

    REVIEW_AUTOMATION = ServiceDescription(
        "ReviewNotification"
    )

    WS = ServiceDescription(
        "WS",
        commands=(
            ServiceCommands.reboot,
            ServiceCommands.shutdown,
            ServiceCommands.send_message_to_user_or_workstation,
            ServiceCommands.kill_process,
        ),
    )

    BACKUP = ServiceDescription(
        "Backup",
        commands=(
            ServiceCommands.robocopy_start_job,
            ServiceCommands.robocopy_get_job_status_list,
        ),
        standalone_name="bck",
    )

    PRINTER = ServiceDescription(
        "Printer",
        commands=(ServiceCommands.printers_report, ServiceCommands.printer_snmp_call),
    )
    
    
    ZABBIX = ServiceDescription(
        "Zabbix",
    )
    
    IOTDevices = ServiceDescription(
        "IOTDevices",
    )

    POLIBASE_DATABASE = ServiceDescription(
        "PolibaseDatabase",
        commands=(ServiceCommands.create_polibase_database_backup,),
    )

    SSH = ServiceDescription(
        "SSH",
        commands=(
            ServiceCommands.execute_ssh_command,
            ServiceCommands.get_certificate_information,
            ServiceCommands.get_unix_free_space_information_by_drive_name,
            ServiceCommands.mount_facade_for_linux_host,
        ),
    )

    """
    POLIBASE_PERSON_INFORMATION_QUEST = ServiceDescription(
        "PolibasePersonInformationQuest",
        description="Polibase Person Information Quest service",
        host=Hosts.BACKUP_WORKER.NAME,
        commands=(ServiceCommands.start_polibase_person_information_quest,),
    )
    """

    WS735 = ServiceDescription(
        "ws735",
        description="ws-735 service",
        host=Hosts.WS735.NAME,
        commands=(ServiceCommands.print_image,)
    )

    RECOGNIZE_TEST = ServiceDescription(
        "RecognizeTest",
        description="Recognize test service",
        host=Hosts.WS255.NAME,
        auto_start=False,
        auto_restart=False,
        visible_for_admin=False,
    )

    """INDICATIONS = ServiceDescription(
        "Indications",
        description="Indications service",
        host=HOSTS.WS255.NAME,
    )"""

    MEDICAL_AUTOMATION = ServiceDescription(
        "MedicalAutomation",
        description="Medical Automation service",
        host=Hosts.BACKUP_WORKER.NAME,
    )

    REGISTRATOR_HELPER = ServiceDescription("RegistratorHelper")

    DEVELOPER = ServiceDescription(
        "Developer",
        description="Developer service",
        host=Hosts.DEVELOPER.NAME,
        port=RPC.PORT(1),
        visible_for_admin=False,
        auto_start=False,
        auto_restart=False,
        commands=(ServiceCommands.test,),
    )
