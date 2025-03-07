"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}
    
    # Recherche automatique des tables créées dans cette migration
    tables_created = []
    
    # Parcourir les opérations Alembic pour identifier les CreateTable
    for line in """${upgrades if upgrades else ""}""".split('\n'):
        if 'op.create_table(' in line:
            # Extraction du nom de table entre guillemets après create_table
            import re
            match = re.search(r'op\.create_table\([\'"]([^\'"]+)[\'"]', line)
            if match:
                table_name = match.group(1)
                if table_name != 'alembic_version':
                    tables_created.append(table_name)
    
    # Appliquer RLS aux tables nouvellement créées
    for table in tables_created:
        # Activer RLS
        op.execute(f"ALTER TABLE public.{table} ENABLE ROW LEVEL SECURITY;")
        
        # Créer les politiques de base
        op.execute(f"""
            CREATE POLICY "{table}_auth_select" ON public.{table}
            FOR SELECT USING (
                auth.uid() = owner_id OR
                auth.role() = 'service_role'
            );
        """)
        
        op.execute(f"""
            CREATE POLICY "{table}_auth_insert" ON public.{table}
            FOR INSERT WITH CHECK (
                auth.uid() = owner_id OR
                auth.role() = 'service_role'
            );
        """)
        
        op.execute(f"""
            CREATE POLICY "{table}_auth_update" ON public.{table}
            FOR UPDATE USING (
                auth.uid() = owner_id OR
                auth.role() = 'service_role'
            ) WITH CHECK (
                auth.uid() = owner_id OR
                auth.role() = 'service_role'
            );
        """)
        
        op.execute(f"""
            CREATE POLICY "{table}_auth_delete" ON public.{table}
            FOR DELETE USING (
                auth.uid() = owner_id OR
                auth.role() = 'service_role'
            );
        """)


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
    
    # Recherche des tables supprimées lors du downgrade
    tables_dropped = []
    
    # Parcourir les opérations de downgrade pour identifier les DropTable
    for line in """${downgrades if downgrades else ""}""".split('\n'):
        if 'op.drop_table(' in line:
            import re
            match = re.search(r'op\.drop_table\([\'"]([^\'"]+)[\'"]', line)
            if match:
                table_name = match.group(1)
                if table_name != 'alembic_version':
                    tables_dropped.append(table_name)
    
    # Pour chaque table qui sera supprimée, supprimer d'abord les politiques RLS
    for table in tables_dropped:
        # Supprimer les politiques
        op.execute(f'DROP POLICY IF EXISTS "{table}_auth_select" ON public.{table};')
        op.execute(f'DROP POLICY IF EXISTS "{table}_auth_insert" ON public.{table};')
        op.execute(f'DROP POLICY IF EXISTS "{table}_auth_update" ON public.{table};')
        op.execute(f'DROP POLICY IF EXISTS "{table}_auth_delete" ON public.{table};')
        
        # Désactiver RLS
        op.execute(f'ALTER TABLE public.{table} DISABLE ROW LEVEL SECURITY;')