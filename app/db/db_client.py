import logging
import os

import weaviate
from weaviate.util import generate_uuid5
from dotenv import load_dotenv

load_dotenv()


LOGGER = logging.getLogger('entity-linker')
LOGGER.setLevel(logging.DEBUG)


class DBIndex:
    def __init__(self, class_name, update=False):
        self.client = weaviate.Client(url=os.environ.get('WEAVIATE_URL', "http://localhost:8080"))
        self.class_name = class_name
        self.update = update

    def init(self):
        self._create_schema()
        self._get_count()

    def _get_count(self):
        response = (
            self.client.query
                .aggregate(self.class_name)
                .with_meta_count()
                .do()
        )
        count = response['data']['Aggregate'][self.class_name][0]['meta']['count']
        LOGGER.info(f'Number of objects in index is : {count}')
        return count

    def _create_schema(self):
        schema = {
            "classes": [{
                "class": self.class_name,
                "description": "Contains entities as text along with their embeddings",
                # "vectorizer": "none",
                # "properties": self.properties
            }]
        }
        available_class_names = [e['class'] for e in self.client.schema.get()['classes']]
        LOGGER.info(f'Available class names {available_class_names}')
        if self.class_name in available_class_names:
            if self.update:
                LOGGER.info(f'Found schema name {self.class_name} in {available_class_names}')
                LOGGER.info(f'deleting {self.class_name}')
                self.client.schema.delete_class(self.class_name)
                LOGGER.info(f'creating {self.class_name}')
                self.client.schema.create(schema)
        else:
            LOGGER.info(f'creating {self.class_name}')
            self.client.schema.create(schema)

    def add_data(self, df):
        counter = 0
        with self.client.batch(batch_size=100, dynamic=True, num_workers=2) as batch:
            for ind, (index, row) in enumerate(df.iterrows()):
                counter += 1
                # obj_data = {e['name']: row[e['name']] for e in self.properties}
                row_id = row['id']
                row = row.drop('id')
                obj_data = row.to_dict()
                batch.add_data_object(data_object=obj_data, class_name=self.class_name, uuid=generate_uuid5(row_id))  # , vector=ebd)
                if not (counter % 10000):
                    LOGGER.info(f'Processed {counter} out of {df.shape[0]}')
        LOGGER.info(f'Processed {ind} out of {df.shape[0]}')
        LOGGER.info("Data Added!")

    def search(self, text, properties, limit):
        # response = (
        #     self.client.query
        #         .get(self.class_name, properties)
        #         .with_bm25(
        #         query=text,
        #         properties=properties
        #     )
        #         .with_additional("score")
        #         .with_additional('id')
        #         # .with_additional('vector')
        #         .with_limit(limit)
        #         # .with_autocut(1)
        #         # .with_limit(3)
        #
        #         .do()
        # )
        response = (
            self.client.query
                .get(self.class_name, properties)
                .with_hybrid(
                query=text,
                alpha=1
                # properties=properties
            )
                .with_additional(["score", 'explainScore', 'id'])
                # .with_additional('vector')
                .with_limit(limit)
                # .with_autocut(1)
                # .with_limit(3)

                .do()
        )

        return response['data']['Get'][self.class_name] #json.dumps(response)

    def get_batch_with_cursor(self, limit, properties, cursor=None):
        # TODO can improve this to add the loop and feed the last id to run the function again. but currently this is made just for sanity checks and there is not need to get all the data yet
        query = (
            self.client.query.get(self.class_name, properties)
            # Optionally retrieve the vector embedding by adding `vector` to the _additional fields
            # .with_additional(["id vector"])
            .with_limit(limit)

        )

        if cursor is not None:
            return query.with_after(cursor).do()
        else:
            return query.do()
