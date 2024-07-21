from cognee.infrastructure.databases.relational.config import get_relationaldb_config

def get_task_status(data_ids: [str]):
    relational_config = get_relationaldb_config()
    db_engine = relational_config.database_engine

    formatted_data_ids = ", ".join([f"'{data_id}'" for data_id in data_ids])

    datasets_statuses = db_engine.execute_query(
      f"""SELECT data_id, status
      FROM (
          SELECT data_id, status, ROW_NUMBER() OVER (PARTITION BY data_id ORDER BY created_at DESC) as rn
          FROM cognee.cognee.cognee_task_status
          WHERE data_id IN ({formatted_data_ids})
      ) t
      WHERE rn = 1;"""
    )

    return { dataset["data_id"]: dataset["status"] for dataset in datasets_statuses }
