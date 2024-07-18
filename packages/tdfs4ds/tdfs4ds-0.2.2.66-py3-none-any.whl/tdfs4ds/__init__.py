__version__ = '0.2.2.66'

from tdfs4ds.feature_store.feature_query_retrieval import get_available_entity_id_records

DATA_DOMAIN             = None
SCHEMA                  = None
FEATURE_CATALOG_NAME    = 'FS_FEATURE_CATALOG'
PROCESS_CATALOG_NAME    = 'FS_PROCESS_CATALOG'
DATA_DISTRIBUTION_NAME  = 'FS_DATA_DISTRIBUTION'
FOLLOW_UP_NAME          = 'FS_FOLLOW_UP'
DATA_DISTRIBUTION_TEMPORAL = False
FILTER_MANAGER_NAME     = 'FS_FILTER_MANAGER'

END_PERIOD              = 'UNTIL_CHANGED' #'9999-01-01 00:00:00'
FEATURE_STORE_TIME      = None #'9999-01-01 00:00:00'
FEATURE_VERSION_DEFAULT = 'dev.0.0'
DISPLAY_LOGS            = True
DEBUG_MODE              = False

USE_VOLATILE_TABLE      = True
STORE_FEATURE           = 'MERGE' #'UPDATE_INSERT'
REGISTER_FEATURE        = 'MERGE' #'UPDATE_INSERT'
REGISTER_PROCESS        = 'MERGE' #'UPDATE_INSERT'
BUILD_DATASET_AT_UPLOAD = False

FEATURE_PARTITION_N     = 2000
FEATURE_PARTITION_EACH  = 10

VARCHAR_SIZE            = 1024

import warnings
warnings.filterwarnings('ignore')

import teradataml as tdml
from tdfs4ds.utils.lineage import crystallize_view
from tdfs4ds.utils.filter_management import FilterManager
from tdfs4ds.utils.info import seconds_to_dhms
import tdfs4ds.feature_store
import tdfs4ds.process_store
import tdfs4ds.datasets
import time

import inspect
import tqdm

from tdfs4ds.feature_store.feature_data_processing import generate_on_clause

import uuid

# Generate a UUID
RUN_ID       = str(uuid.uuid4())
PROCESS_TYPE = None

try:
    SCHEMA = tdml.context.context._get_current_databasename()
    if SCHEMA is None:
        print('Please specify the database which is hosting the feature store.')
        print('tdfs4ds.feature_store.schema = "<feature store database>"')
    else:
        print('The default database is used for the feature store.')
        print(f"tdfs4ds.feature_store.schema = '{SCHEMA}'")
        if DATA_DOMAIN is None:
            DATA_DOMAIN = SCHEMA
            print(f"the data domain for the current work is :{DATA_DOMAIN}")
            print("Please update it as you wish with tdfs4ds.DATA_DOMAIN=<your data domain>")

except Exception as e:
    print('Please specify the database which is hosting the feature store.')
    print('tdfs4ds.feature_store.schema = "<feature store database>"')


def setup(database, if_exists='fail'):
    """
    Set up the database environment by configuring schema names and optionally dropping existing tables.

    This function sets the database schema for feature and process catalogs. If specified, it also handles
    the replacement of existing catalog tables. It reports the status of these operations, including any
    encountered exceptions.

    Parameters:
    database (str): The name of the database schema to be used.
    if_exists (str, optional): Determines the behavior if catalog tables already exist in the database.
                               'fail' (default) - Do nothing if the tables exist.
                               'replace' - Drop the tables if they exist before creating new ones.

    Steps performed:
    1. Sets the schema to the provided database name.
    2. If 'if_exists' is 'replace', attempts to drop 'FS_FEATURE_CATALOG' and 'FS_PROCESS_CATALOG' tables.
    3. Creates new feature and process catalog tables and sets their names in the tdfs4ds module.
    4. Prints the names of the newly created tables along with the database name.
    5. Captures and prints the first line of any exceptions that occur during these operations.

    Returns:
    None
    """

    from tdfs4ds.feature_store.feature_store_management import feature_store_catalog_creation
    from tdfs4ds.process_store.process_store_catalog_management import process_store_catalog_creation

    tdfs4ds.SCHEMA = database
    if if_exists == 'replace':
        try:
            tdml.db_drop_table(table_name = tdfs4ds.FEATURE_CATALOG_NAME, schema_name=database)
        except Exception as e:
            print(str(e).split('\n')[0])
        try:
            tdml.db_drop_table(table_name = tdfs4ds.PROCESS_CATALOG_NAME, schema_name=database)
        except Exception as e:
            print(str(e).split('\n')[0])
        try:
            tdml.db_drop_table(table_name = tdfs4ds.DATA_DISTRIBUTION_NAME, schema_name=database)
        except Exception as e:
            print(str(e).split('\n')[0])
    try:
        tdfs4ds.FEATURE_CATALOG_NAME = feature_store_catalog_creation()
        print('feature catalog table: ', tdfs4ds.FEATURE_CATALOG_NAME, ' in database ', database)
    except Exception as e:
        print(str(e).split('\n')[0])

    try:
        tdfs4ds.PROCESS_CATALOG_NAME, tdfs4ds.DATA_DISTRIBUTION_NAME, tdfs4ds.FILTER_MANAGER_NAME = process_store_catalog_creation()
        print('process catalog table: ', tdfs4ds.PROCESS_CATALOG_NAME, ' in database ', database)
        print('data distribution table: ', tdfs4ds.DATA_DISTRIBUTION_NAME, ' in database ', database)
        print('filter manager table: ', tdfs4ds.FILTER_MANAGER_NAME, ' in database ', database)
    except Exception as e:
        print(str(e).split('\n')[0])

    try:
        tdfs4ds.process_store.process_followup.follow_up_table_creation()
    except Exception as e:
        print(str(e).split('\n')[0])

    return

def connect(
    database=tdfs4ds.SCHEMA,
    feature_catalog_name=tdfs4ds.FEATURE_CATALOG_NAME,
    process_catalog_name=tdfs4ds.PROCESS_CATALOG_NAME,
    data_distribution_name=tdfs4ds.DATA_DISTRIBUTION_NAME,
    filter_manager_name=tdfs4ds.FILTER_MANAGER_NAME,
    followup_name=tdfs4ds.FOLLOW_UP_NAME
):
    """
    Configures the database environment by setting schema names and checking the existence of specified catalog tables.

    This function initializes the database schema and verifies the presence of the feature catalog, process catalog,
    data distribution tables, and the filter manager. It updates the module-level configuration for these names if they exist.
    If any of the specified tables or manager do not exist, it raises an assertion error.

    Parameters:
    - database (str): The name of the database schema to use. Defaults to tdfs4ds.SCHEMA.
    - feature_catalog_name (str, optional): The name of the feature catalog table. Defaults to tdfs4ds.FEATURE_CATALOG_NAME.
    - process_catalog_name (str, optional): The name of the process catalog table. Defaults to tdfs4ds.PROCESS_CATALOG_NAME.
    - data_distribution_name (str, optional): The name of the data distribution table. Defaults to tdfs4ds.DATA_DISTRIBUTION_NAME.
    - filter_manager_name (str, optional): The name of the filter manager. Defaults to tdfs4ds.FILTER_MANAGER_NAME.

    Steps Performed:
    1. Set the database schema to the provided 'database' name.
    2. Retrieve the list of tables in the specified schema and check for the existence of the feature catalog, process catalog,
       data distribution tables, and filter manager.
    3. Update the module-level names for these tables and manager if they exist.
    4. Raise an assertion error if any of the specified tables or manager do not exist, specifying which are missing.

    Returns:
    None

    Raises:
    AssertionError: An error indicating which of the feature catalog, process catalog, data distribution table, or filter manager do not exist.
    """
    if database is not None:
        tdfs4ds.SCHEMA = database
    else:
        assert False, "database parameter is None."

    tables = [x.lower() for x in list(tdml.db_list_tables(schema_name=tdfs4ds.SCHEMA, object_type='table').TableName.values)]
    feature_exists = feature_catalog_name.lower() in tables
    process_exists = process_catalog_name.lower() in tables
    distrib_exists = data_distribution_name.lower() in tables
    filter_manager_exists = filter_manager_name.lower() in tables
    followup_name_exists = followup_name.lower() in tables

    if followup_name_exists:
        tdfs4ds.FOLLOW_UP_NAME = followup_name
    else:
        tdfs4ds.process_store.process_followup.follow_up_table_creation()
        tdfs4ds.FOLLOW_UP_NAME = followup_name

    if feature_exists and process_exists and distrib_exists and filter_manager_exists:
        tdfs4ds.FEATURE_CATALOG_NAME = feature_catalog_name
        tdfs4ds.PROCESS_CATALOG_NAME = process_catalog_name
        tdfs4ds.DATA_DISTRIBUTION_NAME = data_distribution_name
        tdfs4ds.FILTER_MANAGER_NAME = filter_manager_name


        process_list = tdml.DataFrame(tdml.in_schema(database, process_catalog_name))
        if 'ENTITY_NULL_SUBSTITUTE' not in process_list.columns:
            print('ENTITY_NULL_SUBSTITUTE column does not exist in the existing process catalog')
            print('upgrade to the latest DDL')
            tdfs4ds.process_store.process_store_catalog_management.upgrade_process_catalog()
    else:
        missing = []
        if not feature_exists:
            missing.append("feature catalog")
        if not process_exists:
            missing.append("process catalog")
        if not distrib_exists:
            missing.append("data distribution table")
        if not filter_manager_exists:
            missing.append("filter manager")
        assert False, f"""{', '.join(missing)} {'do' if len(missing) > 1 else 'does'} not exist.
        Please run setup to create the missing table ou speficy the correct name in the arguments.
        type help(tdfs4ds.connect) for more information."""

    def is_data_distribution_temporal():
        return 'PERIOD' in tdfs4ds.utils.lineage.get_ddl(view_name=tdfs4ds.DATA_DISTRIBUTION_NAME,
                                                         schema_name=tdfs4ds.SCHEMA, object_type='table')

    if is_data_distribution_temporal():
        tdfs4ds.DATA_DISTRIBUTION_TEMPORAL = True
    else:
        tdfs4ds.DATA_DISTRIBUTION_TEMPORAL = False
    return


def feature_catalog():
    """
    Retrieve a list of all features available in the feature store.

    This function queries the feature store to obtain a comprehensive list of features
    that have been defined and stored. It leverages the feature store's query retrieval
    functionality to compile and return this list. This can be useful for understanding
    what features are available for analysis, machine learning models, or other purposes
    within the data ecosystem.

    Returns:
    - list: A list of features available in the feature store as a teradata dataframe at
            the tdfs4ds.FEATURE_STORE_TIME valid time.
    """
    return tdfs4ds.feature_store.feature_query_retrieval.list_features()


def process_catalog():
    """
    Retrieve a list of all processes registered in the process store.

    This function performs a query against the process store to gather a list of all
    processes that have been registered and are administrable. It utilizes the process
    store's process query administration capabilities to fetch and return this list.
    This is useful for users looking to get an overview of the data processing workflows,
    transformations, and other processes that have been established within the data
    infrastructure.

    Returns:
    - list: A list of processes registered in the process store as a teradata dataframe at
            the tdfs4ds.FEATURE_STORE_TIME valid time.
    """
    return tdfs4ds.process_store.process_query_administration.list_processes()



def run(process_id, return_dataset = False):
    """
    Executes a specific process from the feature store identified by the process ID.
    The function handles different process types and performs appropriate actions.

    Args:
    process_id (str): The unique identifier of the process to run.
    as_date_of (str, optional): Date parameter for the process execution. Defaults to None.

    Returns:
    None: The function returns None, but performs operations based on process type.
    """

    if tdfs4ds.PROCESS_TYPE is None:
        PROCESS_TYPE_ = 'RUN PROCESS'
        tdfs4ds.RUN_ID       = str(uuid.uuid4())
    else:
        PROCESS_TYPE_ = tdfs4ds.PROCESS_TYPE

    if tdfs4ds.DEBUG_MODE:
        print('def run','tdfs4ds.FEATURE_STORE_TIME', tdfs4ds.FEATURE_STORE_TIME)

    if tdfs4ds.FEATURE_STORE_TIME == None:
        validtime_statement = 'CURRENT VALIDTIME'
    else:
        validtime_statement = f"VALIDTIME AS OF TIMESTAMP '{tdfs4ds.FEATURE_STORE_TIME}'"

    # Construct SQL query to retrieve process details by process ID
    query = f"""
    {validtime_statement}
    SEL 
        A.*,
        B.FOR_PRIMARY_INDEX,
        CASE WHEN B.FOR_DATA_PARTITIONING IS NULL THEN '' ELSE B.FOR_DATA_PARTITIONING END AS FOR_DATA_PARTITIONING,
        D.DATABASE_NAME AS FILTER_DATABASE_NAME,
        D.VIEW_NAME AS FILTER_VIEW_NAME,
        D.TABLE_NAME AS FILTER_TABLE_NAME
    FROM {tdfs4ds.SCHEMA}.{tdfs4ds.PROCESS_CATALOG_NAME} A
    LEFT JOIN {tdfs4ds.SCHEMA}.{tdfs4ds.DATA_DISTRIBUTION_NAME} B
    ON A.PROCESS_ID = B.PROCESS_ID
    LEFT JOIN {tdfs4ds.SCHEMA}.{tdfs4ds.FILTER_MANAGER_NAME} D
    ON A.PROCESS_ID = D.PROCESS_ID
    WHERE A.PROCESS_ID = '{process_id}' 
    """

    # Executing the query and converting the result to Pandas DataFrame
    df = tdml.DataFrame.from_query(query).to_pandas()

    # Check if exactly one record is returned, else print an error
    if df.shape[0] != 1:
        print('error - there is ', df.shape[0], f' records. Check table {tdfs4ds.SCHEMA}.{tdfs4ds.PROCESS_CATALOG_NAME}')
        print('check ou this query:')
        print(query)
        return


    # Fetching the filter manager
    filter_schema_name = df['FILTER_DATABASE_NAME'].values[0]
    if filter_schema_name is None:
        filtermanager = None
    else:
        filter_view_name = df['FILTER_VIEW_NAME'].values[0]
        filter_table_name = df['FILTER_TABLE_NAME'].values[0]
        filtermanager = FilterManager(table_name=filter_view_name, schema_name=filter_schema_name)


    tdfs4ds.process_store.process_followup.followup_open(
        run_id        = tdfs4ds.RUN_ID,
        process_type  = PROCESS_TYPE_,
        process_id    = process_id,
        filtermanager = filtermanager
    )


    # Fetching the process type from the query result
    process_type = df['PROCESS_TYPE'].values[0]

    # Fetching the primary index from the query result
    primary_index = df['FOR_PRIMARY_INDEX'].values[0]
    if primary_index is not None:
        primary_index = primary_index.split(',')

    # Fetching the primary index from the query result
    partitioning = df['FOR_DATA_PARTITIONING'].values[0]

    # Fetching the data domain from the query result
    DATA_DOMAIN = df['DATA_DOMAIN'].values[0]

    # Handling 'denormalized view' process type
    if process_type == 'denormalized view':
        # Extracting necessary details for this process type
        view_name = df['VIEW_NAME'].values[0]
        entity_id = eval(df['ENTITY_ID'].values[0])
        entity_null_substitute = eval(df['ENTITY_NULL_SUBSTITUTE'].values[0])
        feature_names = df['FEATURE_NAMES'].values[0].split(',')

        # Fetching data and uploading features to the feature store
        df_data = tdml.DataFrame(tdml.in_schema(view_name.split('.')[0], view_name.split('.')[1]))

        if tdfs4ds.DEBUG_MODE:
            print('run','entity_id',entity_id)
            print('run', 'entity_null_substitute', entity_null_substitute)
            print('run','feature_names',feature_names)
            print('run','process_id',process_id)
            print('run','primary_index',primary_index)
            print('run','partitioning',partitioning)
        dataset = _upload_features(
            df_data,
            entity_id,
            feature_names,
            feature_versions = process_id,
            primary_index = primary_index,
            partitioning = partitioning,
            filtermanager = filtermanager,
            entity_null_substitute = entity_null_substitute
        )

    # Handling 'tdstone2 view' process type
    elif process_type == 'tdstone2 view':
        print('not implemented yet')

    tdfs4ds.process_store.process_followup.followup_close(
        run_id       = tdfs4ds.RUN_ID,
        process_type = PROCESS_TYPE_,
        process_id   = process_id
    )

    if return_dataset:
        return dataset
    else:
        return

def upload_features(df, entity_id, feature_names, metadata={}, primary_index = None, partitioning = '', filtermanager = None, entity_null_substitute = {}):
    """
    Uploads feature data from a DataFrame to the feature store for a specified entity. This involves registering the
    process in the feature store, executing the necessary SQL to insert the data, and returning the resulting dataset
    for further use or inspection.

    The function supports dynamic entity ID interpretation and flexible feature name handling, ensuring compatibility
    with various data schemas. It automatically registers the data upload process and applies additional metadata,
    if provided.

    Parameters:
    - df (DataFrame): The DataFrame containing the feature data to be uploaded.
    - entity_id (dict, list, or str): The identifier of the entity to which the features belong. This can be:
        - a dictionary mapping column names to their data types,
        - a list of column names, which will be automatically converted to a dictionary with types inferred from `df`,
        - a string representing a single column name, which will be converted into a list and then to a dictionary as above.
    - feature_names (list or str): The names of the features to be uploaded. If a string is provided, it will be
      split into a list based on commas or treated as a single feature name.
    - metadata (dict, optional): Additional metadata to associate with the upload process. Defaults to an empty dictionary.
    - primary_index (list, optional): Specifies the primary index columns for optimizing data storage and retrieval.
    - partitioning (str, optional): Defines how the data should be partitioned in the store for performance optimization.

    Returns:
    DataFrame: A DataFrame representing the dataset resulting from the upload process, typically used for validation
               or further processing.

    The process involves several steps, including entity ID type conversion if necessary, feature name normalization,
    process registration in the feature store, and the execution of SQL queries to insert the data. The function concludes
    by returning a dataset derived from the uploaded data, offering immediate access to the newly stored information.

    Example:
    >>> df = tdml.DataFrame(...)
    >>> entity_id = ['customer_id']
    >>> feature_names = ['age', 'income']
    >>> dataset = upload_features(df, entity_id, feature_names)
    >>> # Another example with list-based entity_id, custom primary_index, and partitioning
    >>> tddf = tdml.DataFrame(...)  # Assuming tddf is predefined with appropriate columns
    >>> entity_id = ['tx_type', 'txn_id']
    >>> primary_index = ['txn_id']
    >>> partitioning = '''
    ... PARTITION BY CASE_N (
    ...     tx_type LIKE 'DEBIT',
    ...     tx_type LIKE 'PAYMENT',
    ...     tx_type LIKE 'CASH_OUT',
    ...     tx_type LIKE 'CASH_IN',
    ...     tx_type LIKE 'TRANSFER',
    ...     NO CASE,
    ...     UNKNOWN)'''
    >>> features = [x for x in tddf.columns if x not in entity_id]
    >>> dataset = upload_features(
    ...     df = tddf,
    ...     entity_id = entity_id,
    ...     feature_names = features,
    ...     metadata = {'project': 'test'},
    ...     primary_index = primary_index,
    ...     partitioning = partitioning
    ... )
    """

    from tdfs4ds.utils.info import get_column_types
    from tdfs4ds.utils.query_management import execute_query
    from tdfs4ds.process_store.process_registration_management import register_process_view

    # Convert entity_id to a dictionary if it's not already one
    if type(entity_id) == list:
        entity_id.sort()
        entity_id = get_column_types(df, entity_id)
        if tdfs4ds.DISPLAY_LOGS:
            print('entity_id has been converted to a proper dictionary : ', entity_id)
    elif type(entity_id) == str:
        entity_id = [entity_id]
        entity_id = get_column_types(df, entity_id)
        if tdfs4ds.DISPLAY_LOGS:
            print('entity_id has been converted to a proper dictionary : ', entity_id)

    if type(feature_names) != list:
        if tdfs4ds.DISPLAY_LOGS:
            print('feature_names is not a list:', feature_names)
        if ',' in feature_names:
            feature_names = feature_names.split(',')
        else:
            feature_names = [feature_names]
        if tdfs4ds.DISPLAY_LOGS:
            print('it has been converted to : ', feature_names)
            print('check it is a expected.')

    if primary_index is not None and type(primary_index) != list:
        if tdfs4ds.DISPLAY_LOGS:
            print('primary_index is not a list:', primary_index)
        if ',' in primary_index:
            primary_index = primary_index.split(',')
        else:
            primary_index = [primary_index]
        if tdfs4ds.DISPLAY_LOGS:
            print('it has been converted to : ', feature_names)
            print('check it is a expected.')

    partitioning = tdfs4ds.utils.info.generate_partitioning_clause(partitioning=partitioning)

    if tdfs4ds.DISPLAY_LOGS:
        print("filtermanager", filtermanager)

    # Register the process and retrieve the SQL query to insert the features, and the process ID
    query_insert, process_id, query_insert_dist, query_insert_filtermanager = register_process_view.__wrapped__(
        view_name       = df,
        entity_id       = entity_id,
        feature_names   = feature_names,
        metadata        = metadata,
        with_process_id = True,
        primary_index   = primary_index,
        partitioning    = partitioning,
        filtermanager   = filtermanager,
        entity_null_substitute = entity_null_substitute
    )

    # Execute the SQL query to insert the features into the database
    execute_query(query_insert)
    execute_query(query_insert_dist)
    if tdfs4ds.DEBUG_MODE:
        print("query_insert_filtermanager",query_insert_filtermanager)
    if query_insert_filtermanager is not None:
        execute_query(query_insert_filtermanager)

    # Run the registered process and return the resulting dataset
    tdfs4ds.PROCESS_TYPE = 'UPLOAD_FEATURES'
    if tdfs4ds.BUILD_DATASET_AT_UPLOAD: tdfs4ds.PROCESS_TYPE = 'UPLOAD_FEATURES WITH DATASET VALIDATION'
    tdfs4ds.RUN_ID = str(uuid.uuid4())

    if tdfs4ds.BUILD_DATASET_AT_UPLOAD:

        try:

            dataset = run(process_id=process_id, return_dataset=True)

        except Exception as e:
            tdfs4ds.process_store.process_followup.followup_close(
                run_id       = tdfs4ds.RUN_ID,
                process_type = tdfs4ds.PROCESS_TYPE,
                process_id   = process_id,
                status       = 'FAILED,' + str(e).split('\n')[0]
            )


        return dataset
    else:

        try:
            run(process_id=process_id, return_dataset=False)
        except Exception as e:
            tdfs4ds.process_store.process_followup.followup_close(
                run_id       = tdfs4ds.RUN_ID,
                process_type = tdfs4ds.PROCESS_TYPE,
                process_id   = process_id,
                status       = 'FAILED,' + str(e).split('\n')[0]
            )
        return

    tdfs4ds.PROCESS_TYPE = None

def _upload_features(df, entity_id, feature_names,
                   feature_versions=FEATURE_VERSION_DEFAULT, primary_index = None, partitioning = '', filtermanager=None, entity_null_substitute={}):
    """
    Uploads features from a DataFrame to the feature store, handling entity registration, feature type determination,
    feature registration, preparation for ingestion, and storage in the designated feature tables.

    Parameters:
    - df (DataFrame): The input DataFrame containing the feature data.
    - entity_id (str or dict): The identifier for the entity to which these features belong. This can be a single ID
                               (str) or a dictionary of attribute names and values uniquely identifying the entity.
    - feature_names (list): A list of strings specifying the names of the features to be uploaded.
    - feature_versions (str or list, optional): Specifies the versions of the features to be uploaded. Can be a single
                                                string applied to all features or a list of strings specifying the version
                                                for each feature respectively. Default is 'dev.0.0'.
    - primary_index (list, optional): Specifies the columns to be used as the primary index in the feature store tables.
                                      This can significantly impact the performance of data retrieval operations.
    - partitioning (str, optional): A string indicating the partitioning strategy for the feature store tables, which can
                                    enhance query performance based on the access patterns.

    Returns:
    DataFrame: A DataFrame representing the dataset view created in the feature store, detailing the features and their
               metadata, including versions and storage locations.

    This function orchestrates several steps involved in feature storage:
    1. Registers the entity in the feature store if not already present.
    2. Determines the data types of the features based on the input DataFrame.
    3. Registers the features, including their names, types, and versions, in the feature catalog.
    4. Prepares the feature data for ingestion, including any necessary transformations.
    5. Stores the prepared feature data in the feature store.
    6. Optionally, cleans up temporary resources used during the process.
    7. Builds and returns a view of the dataset representing the uploaded features for easy access.

    Note:
    - The function relies on various sub-modules within the `tdfs4ds` library for different steps of the process, from
      entity and feature registration to data preparation and storage.
    - It is intended to be used internally within a system that manages a Teradata feature store, assuming access to
      a Teradata database and the appropriate schema for feature storage.
    - The function assumes that the feature_versions, if provided as a list, matches the length of feature_names.
    """
    from tdfs4ds.feature_store.entity_management        import register_entity
    from tdfs4ds.feature_store.feature_store_management import Gettdtypes
    from tdfs4ds.feature_store.feature_store_management import register_features
    from tdfs4ds.feature_store.feature_data_processing  import prepare_feature_ingestion
    from tdfs4ds.feature_store.feature_data_processing  import store_feature

    register_entity(entity_id, primary_index=primary_index, partitioning=partitioning)

    # If feature_versions is a list, create a dictionary mapping each feature name to its corresponding version.
    # If feature_versions is a string, create a dictionary mapping each feature name to this string.
    if type(feature_versions) == list:
        selected_features = {k: v for k, v in zip(feature_names, feature_versions)}
    else:
        selected_features = {k: feature_versions for k in feature_names}

    # Get the Teradata types of the features in df.
    feature_names_types = Gettdtypes(
        df,
        features_columns=feature_names,
        entity_id=entity_id
    )

    if tdfs4ds.DEBUG_MODE:
        print('_upload_features', 'entity_id',     entity_id)
        print('_upload_features', 'entity_null_substitute', entity_null_substitute)
        print('_upload_features', 'feature_names', feature_names)
        print('_upload_features', 'primary_index', primary_index)
        print('_upload_features', 'partitioning',  partitioning)
        print('_upload_features', 'selected_features', selected_features)
        print('_upload_features', 'df.columns', df.columns)

    # Register the features in the feature catalog.
    register_features(
        entity_id,
        feature_names_types,
        primary_index,
        partitioning
    )
    if tdfs4ds.DEBUG_MODE:
        print("---------_upload_features")
        print("filtermanager     : ", filtermanager)
        print("feature names     : ", feature_names)
        print("selected features : ", selected_features)



    if filtermanager is None:
        # Prepare the features for ingestion.
        prepared_features, volatile_table_name = prepare_feature_ingestion(
            df,
            entity_id,
            feature_names,
            feature_versions=selected_features,
            primary_index=primary_index,
            entity_null_substitute=entity_null_substitute
        )
        # Store the prepared features in the feature store.
        store_feature(
            entity_id,
            prepared_features,
            entity_null_substitute=entity_null_substitute,
            primary_index=primary_index,
            partitioning=partitioning
        )
    else:
        nb_filters = filtermanager.nb_filters
        for i in range(nb_filters):
            filtermanager.update(i+1)
            if tdfs4ds.DISPLAY_LOGS:
                print(filtermanager.display())
            # Prepare the features for ingestion.
            prepared_features, volatile_table_name = prepare_feature_ingestion(
                df,
                entity_id,
                feature_names,
                feature_versions=selected_features,
                primary_index=primary_index,
                entity_null_substitute=entity_null_substitute
            )

            # Store the prepared features in the feature store.
            store_feature(
                entity_id,
                prepared_features,
                entity_null_substitute=entity_null_substitute,
                primary_index = primary_index,
                partitioning = partitioning

            )

            # Clean up by dropping the temporary volatile table.
            tdml.execute_sql(f'DROP TABLE {volatile_table_name}')

    # Build a dataset view in the feature store.
    if tdfs4ds.BUILD_DATASET_AT_UPLOAD:
        if tdfs4ds.DISPLAY_LOGS: print('build dataset for validation')
        try:
            dataset = build_dataset(
                entity_id,
                selected_features,
                view_name=None,
                entity_null_substitute = entity_null_substitute
            )
        except Exception as e:
            print('ERROR at build_dataset in _upload_features:')
            print(str(e).split('\n')[0])
            print('entity :', entity_id)
            print('selected features :', selected_features)

        # Return the dataset view.
        return dataset
    else:
        if tdfs4ds.DISPLAY_LOGS: print('no dataset built for validation. Set tdfs4ds.BUILD_DATASET_AT_UPLOAD to True if you want it')
        return

# def build_dataset_old(entity_id, selected_features, view_name, schema_name = tdfs4ds.SCHEMA,
#                   comment='dataset', no_temporal=False, time_manager=None, query_only=False):
#     """
#     This function builds a dataset view in a Teradata database. It is designed to pivot and format data from the feature catalog and feature tables based on the specified parameters.
#
#     Parameters:
#     - entity_id (dict or list or other): A dictionary, list, or other format representing the entity ID. The keys of the dictionary are used to identify the entity. Lists and other formats are converted to a list of keys.
#     - selected_features (dict): A dictionary specifying the selected features and their corresponding feature versions.
#     - view_name (str): The name of the dataset view to be created.
#     - comment (str, optional): A comment to associate with the dataset view. Defaults to 'dataset'.
#     - no_temporal (bool, optional): Flag to determine if temporal aspects should be ignored. Defaults to False.
#     - time_manager (object, optional): An object to manage time aspects. Defaults to None.
#     - query_only (bool, optional): Flag to determine if we want only the generated query without the execution
#
#     Returns:
#     tdml.DataFrame: A DataFrame representing the dataset view.
#     """
#
#     from tdfs4ds.utils.query_management import execute_query
#
#     # Retrieve feature data from the feature catalog table
#     feature_catalog = tdml.DataFrame.from_query(f'CURRENT VALIDTIME SELECT * FROM {tdfs4ds.SCHEMA}.{tdfs4ds.FEATURE_CATALOG_NAME}')
#
#     # Determine the valid time statement based on the presence of a specific date in the past
#     if tdfs4ds.FEATURE_STORE_TIME is None:
#         validtime_statement = 'CURRENT VALIDTIME'
#     else:
#         validtime_statement = f"VALIDTIME AS OF TIMESTAMP '{tdfs4ds.FEATURE_STORE_TIME}'"
#
#     # Adjust valid time statement based on the presence of time_manager and no_temporal flag
#     if no_temporal:
#         validtime_statement = ''
#
#     # Convert entity_id to a list format for processing
#     if isinstance(entity_id, list):
#         list_entity_id = entity_id
#     elif isinstance(entity_id, dict):
#         list_entity_id = list(entity_id.keys())
#     else:
#         list_entity_id = [entity_id]
#
#     list_entity_id.sort()
#
#     # Compose the entity names and retrieve the corresponding feature locations
#     ENTITY_NAMES = ','.join([k for k in list_entity_id])
#     ENTITY_ID = ', \n'.join([k for k in list_entity_id])
#     if len(selected_features) > 1:
#         ENTITY_ID_ = ','.join([','.join(['COALESCE('+','.join(['AA'+str(i+1)+'.'+k for i,c in enumerate(selected_features)])+') as '+k]) for k in list_entity_id])
#     else:
#         ENTITY_ID_ = ','.join([','.join(['' + ','.join(['AA' + str(i + 1) + '.' + k for i, c in enumerate(selected_features)]) + ' as ' + k]) for k in list_entity_id])
#
#
#     feature_location = feature_catalog[(feature_catalog.FEATURE_NAME.isin(list(selected_features.keys()))) & \
#                                         (feature_catalog.ENTITY_NAME == ENTITY_NAMES) & \
#                                         (feature_catalog.DATA_DOMAIN == tdfs4ds.DATA_DOMAIN) \
#                                        ].to_pandas()
#
#
#
#     # manage the case sensitivity
#     feature_location['FEATURE_NAME_UPPER'] = [x.upper() for x in feature_location['FEATURE_NAME']]
#     feature_location['FEATURE_VERSION'] = feature_location['FEATURE_NAME_UPPER'].map({k.upper():v for k,v in selected_features.items()})
#
#
#     # Build the query to retrieve the selected features from the feature tables
#     query = []
#     counter = 1
#     feature_names = []
#     for g,df in feature_location.groupby(['FEATURE_DATABASE','FEATURE_VIEW']):
#         for i,row in df.iterrows():
#             condition = ' \n '+f"(FEATURE_ID = {row['FEATURE_ID']} AND FEATURE_VERSION = '{row['FEATURE_VERSION']}')"
#             if time_manager is not None:
#                 if 'date' in time_manager.data_type.lower():
#                     if tdfs4ds.DISPLAY_LOGS:
#                         print(f'Time Manager {time_manager.schema_name}.{time_manager.table_name} has a {time_manager.data_type} data type')
#                     query_ = f"""
#                     SELECT  A{counter}.* FROM (
#                     SELECT * FROM {g[0]}.{g[1]}
#                     WHERE  {condition} AND PERIOD(CAST(ValidStart AS DATE), CAST(ValidEnd AS DATE)) CONTAINS (SEL BUSINESS_DATE FROM {time_manager.schema_name}.{time_manager.view_name})
#                     ) A{counter}
#                     """
#                 else:
#                     if tdfs4ds.DISPLAY_LOGS:
#                         print(
#                         f'Time Manager {time_manager.schema_name}.{time_manager.table_name} has a {time_manager.data_type} data type')
#                     query_ = f"""
#                     SELECT  A{counter}.* FROM (
#                     SELECT * FROM {g[0]}.{g[1]}
#                     WHERE  {condition} AND PERIOD(ValidStart, ValidEnd) CONTAINS (SEL BUSINESS_DATE FROM {time_manager.schema_name}.{time_manager.view_name})
#                     ) A{counter}
#                     """
#             else:
#                 query_ = f"""
#                 SELECT  A{counter}.* FROM (
#                 {validtime_statement} SELECT * FROM {g[0]}.{g[1]}
#                 WHERE  {condition}
#                 ) A{counter}
#                 """
#             query.append(query_)
#             feature_names.append(row['FEATURE_NAME'])
#             counter+=1
#
#
#
#     query_select  = [f"SELECT {ENTITY_ID_}"]
#     query_select  = query_select + ['AA'+str(i+1)+'.FEATURE_VALUE AS '+c for i,c in enumerate(feature_names)]
#     if no_temporal:
#         query_select = query_select + ['AA'+str(i+1)+'.ValidStart AS ValidStart_'+ c + ',AA'+str(i+1)+'.ValidEnd AS ValidEnd_'+ c for i,c in enumerate(feature_names)]
#     query_select  = ', \n'.join(query_select)
#
#     query_from    = [' FROM ('+query[0]+') AA1 ']
#     query_from    = query_from + [' FULL OUTER JOIN ('+q+') AA'+str(i+1)+' \n ON '+' \n AND '.join([f'AA1.{c}=AA{i+1}.{c}' for c in list_entity_id]) for i,q in enumerate(query) if i>0]
#     query_from    = '\n'.join(query_from)
#
#     query_dataset = query_select + '\n' + query_from
#
#     # Build the query to create the dataset view by pivoting the feature data
#     query_create_view = f'''REPLACE VIEW {schema_name}.{view_name}
#     AS LOCK ROW FOR ACCESS '''
#     query_pivot = f"""
#     {query_dataset}
#     """
#
#     if tdml.display.print_sqlmr_query:
#         print(query_create_view+'\n'+query_pivot)
#     if query_only:
#         return query_pivot
#     else:
#         if view_name != None:
#             execute_query(query_create_view+'\n'+query_pivot)
#             execute_query(f"COMMENT ON VIEW {schema_name}.{view_name} IS '{comment}'")
#             if tdfs4ds.DISPLAY_LOGS: print(f'the dataset view {schema_name}.{view_name} has been created')
#
#             return tdml.DataFrame(tdml.in_schema(schema_name, view_name))
#         else:
#             return tdml.DataFrame.from_query(query_pivot)


def build_dataset(entity_id, selected_features, view_name, schema_name=tdfs4ds.SCHEMA,
                  comment='dataset', no_temporal=False, time_manager=None, query_only=False, entity_null_substitute={},
                  other=None, time_column=None
                  ):
    """
    Build a dataset by retrieving and pivoting feature data for given entity IDs.

    Parameters:
    entity_id (list, dict, or str): The entity IDs for which the dataset is to be built. Can be a list, dictionary, or string.
    selected_features (dict): A dictionary of selected features with their versions.
    view_name (str): The name of the view to be created.
    schema_name (str, optional): The schema name where the view will be created. Defaults to tdfs4ds.SCHEMA.
    comment (str, optional): A comment for the dataset. Defaults to 'dataset'.
    no_temporal (bool, optional): Flag to indicate if temporal data should be excluded. Defaults to False.
    time_manager (optional): Time manager for handling temporal aspects. Defaults to None.
    query_only (bool, optional): If True, only return the query string without executing it. Defaults to False.

    Returns:
    str or DataFrame: A SQL query string if query_only is True, otherwise a DataFrame of the created dataset view.
    """

    if schema_name is None:
        print('speficy a schema_name since it is None')
        return

    if tdfs4ds.FEATURE_STORE_TIME is None:
        validtime_statement = 'CURRENT VALIDTIME'
    else:
        validtime_statement = f"VALIDTIME AS OF TIMESTAMP '{tdfs4ds.FEATURE_STORE_TIME}'"

    if no_temporal:
        print('this feature is not yet implemented')

    if other is not None:
        if time_manager is not None:
            print('time_manager should be set to None')
            print('no dataset created/updated')
            return
        if time_column is None:
            print('specify a the time_column')
            print('no dataset created/updated')
            return
        if time_column not in other.columns:
            print(f"'{time_column}' is not a valid column")
            print(f"valid columns are : {other.column}")
            return
        other._DataFrame__execute_node_and_set_table_name(other._nodeid, other._metaexpr)

    # Get the available entity ID records and the list of features
    if other is None:
        query_available_features, list_features = get_available_entity_id_records(entity_id, selected_features)
    else:
        query_available_features, list_features = get_available_entity_id_records(entity_id, selected_features,
                                                                                  other=other, time_column=time_column)

    # Convert entity_id to a list format for processing
    if isinstance(entity_id, list):
        list_entity_id = entity_id
    elif isinstance(entity_id, dict):
        list_entity_id = list(entity_id.keys())
    else:
        list_entity_id = [entity_id]

    # Sort the entity ID list
    list_entity_id.sort()

    query = []
    if time_manager is None:
        if other is None:
            if tdfs4ds.DEBUG_MODE: print('no time manager')
            time_condition = ''
        else:
            if tdfs4ds.DEBUG_MODE: print('time series time condition')
            if 'date' in tdfs4ds.utils.info.get_column_types(df=other, columns=time_column)[time_column].lower():
                time_condition = f"AND PERIOD(CAST(ValidStart AS DATE), CAST(ValidEnd AS DATE)) CONTAINS A2.{time_column}"
            else:
                time_condition = f"AND PERIOD(ValidStart, ValidEnd) CONTAINS A2.{time_column}"

    elif 'date' in time_manager.data_type.lower():
        validtime_statement = ''
        time_condition = f' AND PERIOD(CAST(ValidStart AS DATE), CAST(ValidEnd AS DATE)) CONTAINS (SEL BUSINESS_DATE FROM {time_manager.schema_name}.{time_manager.view_name})'
        if tdfs4ds.DEBUG_MODE:
            print('time manager')
            print('no validtime statement')
            print('time_condition', time_condition)
    else:
        validtime_statement = ''
        time_condition = f' AND PERIOD(ValidStart, ValidEnd) CONTAINS (SEL BUSINESS_DATE FROM {time_manager.schema_name}.{time_manager.view_name})'
        if tdfs4ds.DEBUG_MODE:
            print('time manager')
            print('no validtime statement')
            print('time_condition', time_condition)

    for k, v in list_features.items():
        # Construct the WHERE clause for the query
        txt_where = ' OR '.join(
            [f"(FEATURE_ID = {feature_id} AND FEATURE_VERSION='{feature_version}')" for feature_id, feature_version, _
             in v])
        # Construct the entity ID part of the query
        txt_entity = '\n ,'.join(list_entity_id)
        txt_output = '\n,'.join([c + "_FEATURE_VALUE AS " + c for _, _, c in v])
        # Append the query for the current feature location
        if other is None:
            print('other is None')
            query.append(
                f"""
SEL
{txt_entity}
  ,{txt_output}
FROM (
    {validtime_statement}
    SELECT 
      {txt_entity}
      , FEATURE_NAME
      , FEATURE_VALUE
    FROM {k}
    WHERE ({txt_where})
    {time_condition}
    ) AS A
PIVOT (
  MAX(FEATURE_VALUE) AS FEATURE_VALUE
  FOR FEATURE_NAME IN({','.join(["'" + c + "' AS " + c for _, _, c in v])})
) AS DT
"""
            )
        else:
            print('other is not None')
            query.append(
                f"""
SELECT 
  {time_column}
  ,{txt_entity}
  ,{txt_output}
FROM (
    SELECT 
      A2.{time_column}
      ,{txt_entity}
      , FEATURE_NAME
      , FEATURE_VALUE
    FROM {k} A1
    , {other._table_name} A2
    WHERE ({txt_where})
    {time_condition}
    ) AS A
PIVOT (
  MAX(FEATURE_VALUE) AS FEATURE_VALUE
  FOR FEATURE_NAME IN({','.join(["'" + c + "' AS " + c for _, _, c in v])})
) AS DT
"""
            )
    # Construct the final query by joining individual feature queries
    entity_null_substitute

    txt_entity = []
    for c in list_entity_id:
        if c in entity_null_substitute.keys() and type(entity_null_substitute[c]) == str:
            txt_entity.append(f"CASE WHEN A.{c} = '{entity_null_substitute[c]}' THEN NULL ELSE A.{c} END AS {c}")
        elif c in entity_null_substitute.keys():
            txt_entity.append(f"CASE WHEN A.{c} = {entity_null_substitute[c]} THEN NULL ELSE A.{c} END AS {c}")
        else:
            txt_entity.append('A.' + c)

    txt_entity = '\n ,'.join(txt_entity)
    if other is None:
        query_final = f"""
SELECT
  {txt_entity}
"""
    else:
        query_final = f"""
SELECT
  A.{time_column},{txt_entity}
"""
    counter = 1
    for k, v in list_features.items():
        query_final += '\n ,' + '\n,'.join(['A' + str(counter) + '.' + c for _, _, c in v])
        counter += 1

    query_final += f'\nFROM ({query_available_features}) A \n'

    counter = 1
    for (k, v), q in zip(list_features.items(), query):
        query_final += f'LEFT JOIN ({q}) A{counter} \n'
        query_final += f'ON {" AND ".join(["A." + e + "=A" + str(counter) + "." + e for e in list_entity_id])}\n'
        if other is not None:
            query_final += f"AND A.{time_column} = A{counter}.{time_column}\n"
        counter += 1

    where_clause = []
    for i in range(len(query)):
        where_clause.append(f"A{i+1}.{list_entity_id[0]} IS NOT NULL")
    where_clause = 'WHERE ' + '\nAND '.join(where_clause)

    if query_only:
        return query_final + '\n' + where_clause
    else:
        # Build the query to create the dataset view by pivoting the feature data
        query_create_view = f'''
REPLACE VIEW {schema_name}.{view_name} 
AS LOCK ROW FOR ACCESS
{query_final}
{where_clause}
        '''
        if tdfs4ds.DEBUG_MODE: print(query_create_view)
        tdml.execute_sql(query_create_view)
        return tdml.DataFrame(tdml.in_schema(schema_name, view_name))


# def build_dataset_pivoting(entity_id, selected_features, view_name, schema_name=tdfs4ds.SCHEMA,
#                    comment='dataset',  time_manager=None, query_only=False, entity_null_substitute = {}):
#     """
#     This function builds a dataset view in a Teradata database. It is designed to pivot and format data from the feature catalog and feature tables based on the specified parameters.
#
#     Parameters:
#     - entity_id (dict or list or other): A dictionary, list, or other format representing the entity ID. The keys of the dictionary are used to identify the entity. Lists and other formats are converted to a list of keys.
#     - selected_features (dict): A dictionary specifying the selected features and their corresponding feature versions.
#     - view_name (str): The name of the dataset view to be created.
#     - comment (str, optional): A comment to associate with the dataset view. Defaults to 'dataset'.
#     - no_temporal (bool, optional): Flag to determine if temporal aspects should be ignored. Defaults to False.
#     - time_manager (object, optional): An object to manage time aspects. Defaults to None.
#     - query_only (bool, optional): Flag to determine if we want only the generated query without the execution
#
#     Returns:
#     tdml.DataFrame: A DataFrame representing the dataset view.
#     """
#
#     from tdfs4ds.utils.query_management import execute_query
#
#     # Retrieve feature data from the feature catalog table
#     feature_catalog = tdml.DataFrame.from_query(
#         f'CURRENT VALIDTIME SELECT * FROM {tdfs4ds.SCHEMA}.{tdfs4ds.FEATURE_CATALOG_NAME}')
#
#     # Determine the valid time statement based on the presence of a specific date in the past
#     if tdfs4ds.FEATURE_STORE_TIME is None:
#         validtime_statement = 'CURRENT VALIDTIME'
#     else:
#         validtime_statement = f"VALIDTIME AS OF TIMESTAMP '{tdfs4ds.FEATURE_STORE_TIME}'"
#
#     # Convert entity_id to a list format for processing
#     if isinstance(entity_id, list):
#         list_entity_id = entity_id
#     elif isinstance(entity_id, dict):
#         list_entity_id = list(entity_id.keys())
#     else:
#         list_entity_id = [entity_id]
#
#     list_entity_id.sort()
#
#     # Compose the entity names and retrieve the corresponding feature locations
#     ENTITY_NAMES = ','.join([k for k in list_entity_id])
#     ENTITY_NAMES2 = ','.join(["'" + k + "'" for k in list_entity_id])
#     ENTITY_ID = ', \n'.join([k for k in list_entity_id])
#
#     feature_location = feature_catalog[(feature_catalog.FEATURE_NAME.isin(list(selected_features.keys()))) & \
#                                        (feature_catalog.ENTITY_NAME == ENTITY_NAMES) & \
#                                        (feature_catalog.DATA_DOMAIN == tdfs4ds.DATA_DOMAIN) \
#                                        ].to_pandas()
#
#     nb_locations = feature_location.groupby(['FEATURE_DATABASE', 'FEATURE_TABLE']).count().shape[0]
#
#     if nb_locations > 1:
#         ENTITY_ID_ = ','.join([','.join(
#             ['COALESCE(' + ','.join(['AA' + str(i + 1) + '.' + k for i in range(nb_locations)]) + ') as ' + k]) for k in
#                                list_entity_id])
#     else:
#         ENTITY_ID_ = ','.join(
#             [','.join(['' + ','.join(['AA' + str(i + 1) + '.' + k for i in range(nb_locations)]) + ' as ' + k]) for k in
#              list_entity_id])
#
#     # manage the case sensitivity
#     feature_location['FEATURE_NAME_UPPER'] = [x.upper() for x in feature_location['FEATURE_NAME']]
#     feature_location['FEATURE_VERSION'] = feature_location['FEATURE_NAME_UPPER'].map(
#         {k.upper(): v for k, v in selected_features.items()})
#
#     # Build the query to retrieve the selected features from the feature tables
#     query = []
#     counter = 1
#     feature_names = []
#     for g, df in feature_location.groupby(['FEATURE_DATABASE', 'FEATURE_VIEW']):
#         condition = []
#         for i, row in df.iterrows():
#             condition.append(f"(A.FEATURE_ID = {row['FEATURE_ID']} AND FEATURE_VERSION = '{row['FEATURE_VERSION']}')")
#         condition = '\n OR '.join(condition)
#
#         FEATURE_NAME = ','.join(["'" + k + "'" for k in df.FEATURE_NAME])
#
#         if time_manager is not None:
#             if 'date' in time_manager.data_type.lower():
#                 if tdfs4ds.DISPLAY_LOGS:
#                     print(
#                         f'Time Manager {time_manager.schema_name}.{time_manager.table_name} has a {time_manager.data_type} data type')
#                 query_ = f"""
#                 SELECT  A{counter}.* FROM (
#                 SELECT A.*, B.FEATURE_NAME FROM {g[0]}.{g[1]} A
#                 INNER JOIN (
#                     SEL FEATURE_ID, FEATURE_NAME, DATA_DOMAIN
#                     FROM {tdfs4ds.SCHEMA}.{tdfs4ds.FEATURE_CATALOG_NAME}
#                     WHERE DATA_DOMAIN = '{tdfs4ds.DATA_DOMAIN}'
#                     AND  PERIOD(CAST(ValidStart AS DATE), CAST(ValidEnd AS DATE)) CONTAINS (SEL BUSINESS_DATE FROM {time_manager.schema_name}.{time_manager.view_name})
#                 ) B
#                 ON A.FEATURE_ID = B.FEATURE_ID
#                 WHERE  ({condition}) AND PERIOD(CAST(ValidStart AS DATE), CAST(ValidEnd AS DATE)) CONTAINS (SEL BUSINESS_DATE FROM {time_manager.schema_name}.{time_manager.view_name})
#                 ) A{counter}
#                 """
#             else:
#                 if tdfs4ds.DISPLAY_LOGS:
#                     print(
#                         f'Time Manager {time_manager.schema_name}.{time_manager.table_name} has a {time_manager.data_type} data type')
#                 query_ = f"""
#                 SELECT  A{counter}.* FROM (
#                 SELECT A.*, B.FEATURE_NAME FROM {g[0]}.{g[1]} A
#                 INNER JOIN (
#                     SEL FEATURE_ID, FEATURE_NAME, DATA_DOMAIN
#                     FROM {tdfs4ds.SCHEMA}.{tdfs4ds.FEATURE_CATALOG_NAME}
#                     WHERE DATA_DOMAIN = '{tdfs4ds.DATA_DOMAIN}'
#                     AND PERIOD(ValidStart, ValidEnd) CONTAINS (SEL BUSINESS_DATE FROM {time_manager.schema_name}.{time_manager.view_name})
#                     ) B
#                 ON A.FEATURE_ID = B.FEATURE_ID
#                 WHERE  ({condition}) AND PERIOD(ValidStart, ValidEnd) CONTAINS (SEL BUSINESS_DATE FROM {time_manager.schema_name}.{time_manager.view_name})
#                 ) A{counter}
#                 """
#         else:
#             query_ = f"""
#             SELECT  A{counter}.* FROM (
#             SELECT A.*, B.FEATURE_NAME FROM ({validtime_statement}  SEL * FROM {g[0]}.{g[1]}) A
#             INNER JOIN (
#                 {validtime_statement}  SEL FEATURE_ID, FEATURE_NAME, DATA_DOMAIN
#                 FROM {tdfs4ds.SCHEMA}.{tdfs4ds.FEATURE_CATALOG_NAME}
#                 WHERE DATA_DOMAIN = '{tdfs4ds.DATA_DOMAIN}'
#             ) B
#             ON A.FEATURE_ID = B.FEATURE_ID
#             WHERE  ({condition})
#             ) A{counter}
#             """
#
#         query__ = f"""
#         SELECT * FROM TD_Pivoting (
#           ON ({query_}) AS InputTable
#           PARTITION BY {ENTITY_NAMES}
#           USING
#           PartitionColumns ({ENTITY_NAMES2})
#           TargetColumns ('Feature_Value')
#           --Accumulate ('survived')
#           PivotColumn('Feature_Name')
#           PivotKeys({FEATURE_NAME})
#         ) AS dt
#         """
#         query.append(query__)
#         feature_names += ['AA' + str(counter) + '.FEATURE_VALUE_' + c + ' AS ' + c for c in
#                           FEATURE_NAME.replace("'", '').split(',')]
#         counter += 1
#
#
#     query_select = [f"SELECT {ENTITY_ID_}"]
#     query_select = query_select + feature_names
#
#     query_select = ', \n'.join(query_select)
#
#     query_from = [' FROM (' + query[0] + ') AA1 ']
#     query_from = query_from + [' FULL OUTER JOIN (' + q + ') AA' + str(i + 1) + ' \n ON ' + ' \n AND '.join(
#         [f'AA1.{c}=AA{i + 1}.{c}' for c in list_entity_id]) for i, q in enumerate(query) if i > 0]
#     # query_from = query_from + [' FULL OUTER JOIN (' + q + ') AA' + str(i + 1) + ' \n ON ' +
#     #                           generate_on_clause(entity_id, entity_null_substitute, left_name='AA1', right_name=f'AA{i + 1}') for i, q in enumerate(query) if i > 0]
#
#     query_from = '\n'.join(query_from)
#
#     query_dataset = query_select + '\n' + query_from
#
#     # Build the query to create the dataset view by pivoting the feature data
#     query_create_view = f'REPLACE VIEW {schema_name}.{view_name} AS LOCK ROW FOR ACCESS'
#     query_pivot = f"""
#     {query_dataset}
#     """
#
#     if tdfs4ds.DEBUG_MODE: print('query dataset (query_pivot):', query_pivot)
#
#     if tdml.display.print_sqlmr_query:
#         print(query_create_view + '\n' + query_pivot)
#     if query_only:
#         return query_pivot
#     else:
#         if view_name != None:
#             execute_query(query_create_view + '\n' + query_pivot)
#             execute_query(f"COMMENT ON VIEW {schema_name}.{view_name} IS '{comment}'")
#             if tdfs4ds.DISPLAY_LOGS: print(f'the dataset view {schema_name}.{view_name} has been created')
#
#             return tdml.DataFrame(tdml.in_schema(schema_name, view_name))
#         else:
#             return tdml.DataFrame.from_query(query_pivot)
# def _build_time_series(entity_id, selected_feature, query_only=False, time_manager = None):
#     """
#     Constructs a time series dataset for a given entity and feature.
#     Optionally returns only the query used for dataset construction.
#
#     This is a wrapper around the `build_dataset` function, tailored specifically for time series data by setting temporal parameters to null.
#
#     Args:
#         entity_id (dict): The identifier for the entity for which the dataset is being built.
#         selected_feature (str or list): The feature(s) to be included in the dataset.
#         query_only (bool, optional): If True, returns only the SQL query used for building the dataset, not the dataset itself. Defaults to False.
#
#     Returns:
#         DataFrame or str: The constructed time series dataset as a DataFrame, or the SQL query as a string if query_only is True.
#     """
#
#     # Call the build_dataset function with specific parameters set for time series dataset construction
#     return build_dataset_old(
#         entity_id         = entity_id,  # The identifier for the entity
#         selected_features = selected_feature,  # The feature(s) to be included in the dataset
#         no_temporal       = True,  # Indicates that the dataset should not have a temporal component
#         query_only        = query_only,  # Determines whether to return just the query or the constructed dataset
#         time_manager      = None,  # No time management for the dataset construction
#         view_name         = None  # No specific view name provided
#     )


# def build_dataset_time_series(df, time_column, entity_id, selected_features, query_only=False, time_manager=None):
#     """
#     Constructs a time series dataset based on the specified features and entity_id from the provided dataframe.
#
#     Args:
#         df (DataFrame): The source dataframe.
#         time_column (str): The name of the column in df that represents time.
#         entity_id (dict): A dictionary representing the entity identifier.
#         selected_features (dict): A dictionary with keys as feature names and values as conditions or specifications for those features.
#         query_only (bool, optional): If True, only the SQL query for the dataset is returned. Defaults to False.
#         time_manager (TimeManager, optional): An instance of TimeManager to manage time-related operations. Defaults to None.
#
#     Returns:
#         DataFrame or str: The constructed time series dataset as a DataFrame, or the SQL query as a string if query_only is True.
#     """
#
#     # Convert column names to lowercase for case-insensitive matching
#     col = [c.lower() for c in df.columns]
#
#     # Check if the entity_id keys are present in the dataframe columns
#     #for e in entity_id:
#     #    if e.lower() not in col:
#     #        print(f' {e} is not present in your dataframe')
#     #        print('Here are the columns of your dataframe:')
#     #        print(str(col))
#     #        return  # Exit if any entity_id key is not found
#
#     # Check if the time_column is present in the dataframe columns
#     if time_column.lower() not in col:
#         print(f' {time_column} is not present in your dataframe')
#         print('Here are the columns of your dataframe:')
#         print(str(col))
#         return  # Exit if the time_column is not found
#
#     # Extract and check the data type of the time_column
#     d_ = {x[0]: x[1] for x in df._td_column_names_and_types}
#     time_column_data_type = d_[time_column]
#     if tdfs4ds.DISPLAY_LOGS:
#         print('time column data type :', time_column_data_type)
#     if 'date' not in time_column_data_type.lower() and 'time' not in time_column_data_type.lower():
#         print('the time column of your data frame is neither a date nor a timestamp')
#         return  # Exit if the time_column data type is not date or timestamp
#
#     # Initialize the select query
#     select_query = 'SELECT \n' + ', \n'.join(['A.' + c for c in col]) + '\n'
#
#     # If a time_manager is provided, extract its details
#     if time_manager is not None:
#         tm_datatype = time_manager.data_type.lower()
#         tm_schema = time_manager.schema_name
#         tm_table = time_manager.table_name
#
#     sub_queries_list = []
#     # For each selected feature, build its part of the query
#     for i, (k, v) in enumerate(selected_features.items()):
#         select_query += ', BB' + str(i + 1) + '.' + k + '\n'
#
#         nested_query = _build_time_series(entity_id, {k: v}, query_only=True)
#
#         sub_queries = 'SELECT \n' + '\n ,'.join(entity_id) + '\n ,' + k + '\n'
#
#         # Build the sub_queries based on the presence of a time_manager and the data types of time_column and time_manager
#         if time_manager is None:
#             # there is a time manager
#             if 'date' in tm_datatype:
#                 # the data type of the time column is DATE
#                 sub_queries += f',	CAST(ValidStart_{k} AS DATE) AS ValidStart \n'
#                 sub_queries += f',	CAST(ValidEnd_{k} AS DATE) AS ValidEnd \n'
#             else:
#                 # the data type of the time column is timestamp
#                 sub_queries += f',	CAST(ValidStart_{k} AS TIMESTAMP(0)) AS ValidStart \n'
#                 sub_queries += f',	CAST(ValidEnd_{k} AS TIMESTAMP(0)) AS ValidEnd \n'
#         else:
#             # there is a time manager
#
#             if 'date' in time_column_data_type.lower():
#                 # the data type of the time column is DATE
#                 if 'date' in tm_datatype:
#                     time_cursor = "(BUS_DATE.BUSINESS_DATE + INTERVAL '1' DAY)"
#                     # the data type of the time manager is DATE
#                     sub_queries += f',	CAST(ValidStart_{k} AS DATE) AS ValidStart_ \n'
#                     sub_queries += f",	CASE WHEN CAST(ValidEnd_{k} AS DATE) > {time_cursor} AND CAST(ValidStart_{k} AS DATE) < {time_cursor} THEN {time_cursor} ELSE CAST(ValidEnd_{k} AS DATE) END AS ValidEnd_ \n"
#                 else:
#                     time_cursor = "(BUS_DATE.BUSINESS_DATE + INTERVAL '1' SECOND)"
#                     # the data type of the time manager is timestamp
#                     sub_queries += f',	CAST(ValidStart_{k} AS DATE) AS ValidStart_ \n'
#                     sub_queries += f',	CASE WHEN CAST(ValidEnd_{k} AS DATE) > {time_cursor} AND CAST(ValidStart_{k} AS DATE) < {time_cursor} THEN {time_cursor} ELSE CAST(ValidEnd_{k} AS DATE) END AS ValidEnd_ \n'
#             else:
#                 # the data type of the time column is TIMESTAMP
#                 if 'date' in tm_datatype:
#                     time_cursor = "(BUS_DATE.BUSINESS_DATE + INTERVAL '1' DAY)"
#                     sub_queries += f',	CAST(ValidStart_{k} AS TIMESTAMP(0)) AS ValidStart_ \n'
#                     sub_queries += f',	CASE WHEN CAST(ValidEnd_{k} AS TIMESTAMP(0)) > CAST({time_cursor} AS TIMESTAMP(0)) AND CAST(ValidStart_{k} AS TIMESTAMP(0)) < CAST({time_cursor} AS TIMESTAMP(0)) THEN CAST({time_cursor} AS TIMESTAMP(0)) ELSE CAST(ValidEnd_{k} AS TIMESTAMP(0)) END AS ValidEnd_ \n'
#                 else:
#                     sub_queries += f',	CAST(ValidStart_{k} AS TIMESTAMP(0)) AS ValidStart_ \n'
#                     sub_queries += f',	CASE WHEN CAST(ValidEnd_{k} AS TIMESTAMP(0)) > CAST({time_cursor} AS TIMESTAMP(0)) AND CAST(ValidStart_{k} AS TIMESTAMP(0)) < CAST({time_cursor} AS TIMESTAMP(0)) THEN CAST({time_cursor} AS TIMESTAMP(0)) ELSE CAST(ValidEnd_{k} AS TIMESTAMP(0)) END AS ValidEnd_ \n'
#         sub_queries += ',   PERIOD(ValidStart_, ValidEnd_) as PERIOD_ \n'
#         sub_queries += f'FROM ({nested_query}) tmp{i + 1} \n'
#         if time_manager is not None:
#             sub_queries += f',{tm_schema}.{tm_table} BUS_DATE \n'
#
#         sub_queries += 'WHERE ValidStart_ < ValidEnd_ \n'
#
#         sub_queries = 'LEFT JOIN ( \n' + sub_queries + ') BB' + str(i + 1) + '\n ON '
#
#         sub_queries += '\n  AND '.join(['A.' + c + '=BB' + str(i + 1) + '.' + c for c in entity_id])
#
#
#         #sub_queries += f'\n AND PERIOD(BB{i + 1}.ValidStart_, BB{i + 1}.ValidEnd_) CONTAINS A.{time_column} \n'
#         sub_queries += f'\n AND BB{i + 1}.PERIOD_ CONTAINS A.{time_column} \n'
#
#         sub_queries_list.append(sub_queries)
#
#     # Combine all parts of the query
#     query = select_query + f'FROM ({df.show_query()}) A \n' + '\n --------------- \n'.join(sub_queries_list)
#
#     if tdfs4ds.DEBUG_MODE:
#         print('------------- BUILD DATASET TIMESERIES ---------------')
#         print(query)
#     # If only the query is requested, return it; otherwise, execute the query and return the resulting DataFrame
#     if query_only:
#         return query
#     else:
#         return tdml.DataFrame.from_query(query)

def upload_tdstone2_scores(model):
    """
    Uploads features from a model's predictions to the Teradata feature store. This function handles the entire
    workflow from extracting feature names and types, registering them in the feature catalog, preparing features for ingestion,
    storing them in the feature store, and finally creating a dataset view in the feature store.

    Parameters:
    - model: The model object whose predictions contain features to be uploaded. This model should have methods
      to extract predictions and feature information.

    Returns:
    - DataFrame: A DataFrame representing the dataset view created in the feature store, which includes
      features from the model's predictions.

    Note:
    - The function assumes that the model provides a method `get_model_predictions` which returns a Teradata DataFrame.
    - Entity ID for the model is extracted and registered in the data domain.
    - The function cleans up by dropping the volatile table created during the process.
    - The feature names and their types are extracted from the model's predictions and are registered in the feature catalog.
    """

    from tdfs4ds.feature_store.entity_management import register_entity
    from tdfs4ds.feature_store.entity_management import tdstone2_entity_id
    from tdfs4ds.feature_store.feature_store_management import tdstone2_Gettdtypes
    from tdfs4ds.feature_store.feature_store_management import register_features
    from tdfs4ds.feature_store.feature_data_processing import prepare_feature_ingestion_tdstone2
    from tdfs4ds.feature_store.feature_data_processing import store_feature

    # Extract the entity ID from the existing model.
    entity_id = tdstone2_entity_id(model)

    # Register the entity ID in the data domain.
    register_entity(entity_id)

    # Get the Teradata types of the features from the model's predictions.
    feature_names_types = tdstone2_Gettdtypes(model,entity_id)

    # Register these features in the feature catalog.
    register_features(entity_id, feature_names_types)

    # Prepare the features for ingestion into the feature store.
    if 'score' in [x[0] for x in inspect.getmembers(type(model))]:
        prepared_features, volatile_table_name = prepare_feature_ingestion_tdstone2(
            model.get_model_predictions(),
            entity_id
        )
    else:
        prepared_features, volatile_table_name = prepare_feature_ingestion_tdstone2(
            model.get_computed_features(),
            entity_id
        )

    # Store the prepared features in the feature store.
    store_feature(entity_id, prepared_features)

    # Clean up by dropping the temporary volatile table.
    tdml.execute_sql(f'DROP TABLE {volatile_table_name}')

    # Get the list of selected features for building the dataset view.
    if 'score' in [x[0] for x in inspect.getmembers(type(model))]:
        selected_features = model.get_model_predictions().groupby(['FEATURE_NAME', 'ID_PROCESS']).count().to_pandas()[
            ['FEATURE_NAME', 'ID_PROCESS']].set_index('FEATURE_NAME').to_dict()['ID_PROCESS']
    else:
        selected_features = model.get_computed_features().groupby(['FEATURE_NAME', 'ID_PROCESS']).count().to_pandas()[
            ['FEATURE_NAME', 'ID_PROCESS']].set_index('FEATURE_NAME').to_dict()['ID_PROCESS']

    # Build and return the dataset view in the feature store.
    dataset = build_dataset(entity_id, selected_features, view_name=None)
    return dataset


def roll_out(process_list, time_manager, time_id_start = 1):
    """
    Executes a series of processes for each date in a given list, managing the time and logging settings.

    This function iterates over a list of dates, updating a TimeManager object with each date, and then
    executes a list of processes for that date. It also manages the synchronization of time for a feature store
    and disables display logs during its execution.

    Parameters:
    date_list (list): A list of dates for which the processes need to be executed.
    process_list (list): A list of process IDs that need to be executed for each date.
    time_manager (TimeManager object): An object that manages time-related operations, like updating or retrieving time.

    Side Effects:
    - Sets global variables DISPLAY_LOGS and FEATURE_STORE_TIME.
    - Catches and prints exceptions along with the date on which they occurred.
    """

    #global DISPLAY_LOGS
    #global FEATURE_STORE_TIME

    # Disable display logs
    temp_DISPLAY_LOGS = tdfs4ds.DISPLAY_LOGS
    tdfs4ds.DISPLAY_LOGS = False

    tdfs4ds.PROCESS_TYPE = 'ROLL_OUT'
    tdfs4ds.RUN_ID = str(uuid.uuid4())

    try:

        pbar = tqdm.tqdm(range(time_id_start, time_manager.nb_time_steps+1), desc="Starting")
        # Iterate over each date in the provided list
        for i in pbar:
            # Update the time manager with the new date
            time_manager.update(time_id = i )
            date_ = str(time_manager.display().to_pandas()['BUSINESS_DATE'].values[0])
            pbar.set_description(f"Processing {date_}")
            # Synchronize the time for the feature store with the current date
            tdfs4ds.FEATURE_STORE_TIME = time_manager.get_date_in_the_past()
            pbar.set_description(f"Processing {tdfs4ds.FEATURE_STORE_TIME}")
            if tdfs4ds.DEBUG_MODE:
                print('def roll_out','date_', date_)
                print('def roll_out','time_manager.get_date_in_the_past()', time_manager.get_date_in_the_past())
                print('def roll_out','tdfs4ds.FEATURE_STORE_TIME', tdfs4ds.FEATURE_STORE_TIME)
            # Execute each process in the process list for the current date
            for proc_id in process_list:
                pbar.set_description(f"Processing {date_} process {proc_id}")
                run(process_id=proc_id)

        tdfs4ds.DISPLAY_LOGS = temp_DISPLAY_LOGS
    except Exception as e:
        tdfs4ds.DISPLAY_LOGS = temp_DISPLAY_LOGS
        # If an exception occurs, print the date and the first line of the exception message
        print(date_)
        print(str(e).split('\n')[0])
        tdfs4ds.process_store.process_followup.followup_close(
            run_id       = tdfs4ds.RUN_ID,
            process_type = tdfs4ds.PROCESS_TYPE,
            process_id   = proc_id,
            status       = 'FAILED,' + str(e).split('\n')[0]
        )

    tdfs4ds.PROCESS_TYPE = None
