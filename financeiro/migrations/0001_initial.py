# Generated by Django 5.0.3 on 2024-03-27 15:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PacoteConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ticket_valor_base_brl', models.FloatField(help_text='Apenas números pares')),
                ('pacote_qtd_inicial', models.IntegerField(help_text='Primeiro pacote inicia com quantos tickets?')),
                ('pacote_qtd_multiplicador', models.IntegerField(help_text='Multiplicador de tickets por pacote')),
                ('desconto_pacote_multiplicador', models.IntegerField(help_text='Percentual / fator multiplicador de desconto por pacote')),
                ('desconto_add_bitcoin', models.IntegerField(help_text='Percentual / fator multiplicador de desconto por pacote com pg em btc')),
                ('data_registro', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'Pacotes configs',
            },
        ),
        migrations.CreateModel(
            name='PagamentoInvoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('do_pacote', models.IntegerField(blank=True, null=True)),
                ('btc', models.BooleanField(default=False, help_text='Marque se o pagamento foi em bitcoin')),
                ('pago', models.BooleanField(default=False)),
                ('checkout_id', models.CharField(max_length=100, null=True)),
                ('data_registro', models.DateTimeField(auto_now=True)),
                ('do_config', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='financeiro.pacoteconfig')),
            ],
            options={
                'verbose_name_plural': 'Invoices',
                'ordering': ['-data_registro'],
            },
        ),
    ]
