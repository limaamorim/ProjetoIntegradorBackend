from django.db import migrations

def create_initial_groups(apps, schema_editor):
    # Obtém os modelos necessários através da função apps.get_model
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    # Tenta pegar os modelos do seu app
    try:
        Paciente = apps.get_model('nucleo', 'Paciente')
        LogAuditoria = apps.get_model('nucleo', 'LogAuditoria')
    except LookupError:
        return

    # --- Permissões para o MÉDICO ---
    paciente_ct = ContentType.objects.get_for_model(Paciente)
    try:
        add_paciente = Permission.objects.get(codename='add_paciente', content_type=paciente_ct)
        view_paciente = Permission.objects.get(codename='view_paciente', content_type=paciente_ct)
    except Permission.DoesNotExist:
        add_paciente, view_paciente = None, None

    medico_group, created = Group.objects.get_or_create(name='MEDICO')
    if add_paciente and view_paciente:
        medico_group.permissions.add(add_paciente, view_paciente)

    # --- Permissões para o AUDITOR ---
    log_ct = ContentType.objects.get_for_model(LogAuditoria)
    try:
        view_log = Permission.objects.get(codename='view_logauditoria', content_type=log_ct)
    except Permission.DoesNotExist:
        view_log = None
    
    auditor_group, created = Group.objects.get_or_create(name='AUDITOR')
    if view_log:
        auditor_group.permissions.add(view_log)

class Migration(migrations.Migration):

    dependencies = [
        ('nucleo', '0001_initial'), 
    ]

    operations = [
        migrations.RunPython(create_initial_groups),
    ]