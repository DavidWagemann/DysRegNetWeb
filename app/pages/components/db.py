import os
import time
from collections import defaultdict

from neo4j import GraphDatabase


class NetworkDB:
    def __init__(self):
        uri = "bolt://dysregnet-neo4j:7687"
        pw = os.getenv("DB_PASSWORD", "12345678")
        if os.getenv("DB_PASSWORD") is None:
            uri = "bolt://localhost:7687"
        self.uri = uri
        self.auth = ("neo4j", pw)
        self.driver = GraphDatabase.driver(uri=self.uri, auth=self.auth)

    def close(self):
        self.driver.close()

    def get_gene_ids(self, cancer_id):
        command = f"MATCH (n:{cancer_id}_Gene) RETURN n.gene_id"
        return self.get_value(command)

    def get_cancer_ids(self):
        command = "MATCH (c:Cancer) RETURN c.cancer_id"
        return self.get_value(command)

    def get_neighborhood(self, gene_id, cancer_id):
        query_map = {
            "center": f"MATCH (center:{cancer_id}_Gene{{gene_id: '{gene_id}'}}) RETURN center;",
            "sources": (
                f"MATCH (center:{cancer_id}_Gene{{gene_id: '{gene_id}'}})\n"
                f"MATCH (source:{cancer_id}_Gene) -[:REGULATES]-> (regulation:{cancer_id}_Regulation) -[:REGULATED]-> (center)\n"
                "RETURN  source, regulation"
            ),
            "targets": (
                f"MATCH (center:{cancer_id}_Gene{{gene_id: '{gene_id}'}})\n"
                f"MATCH (center) -[:REGULATES]-> (regulation:{cancer_id}_Regulation) -[:REGULATED]-> (target:{cancer_id}_Gene)\n"
                "RETURN  target, regulation"
            ),
        }
        start = time.time()
        result_map = self.get_data_map(query_map)
        print("Transaction time: " + str(time.time() - start))
        return result_map

    def get_neighborhood_multi(self, gene_ids, cancer_id):
        query_map_list = []
        for gene_id in gene_ids:
            query_map_list.append(
                {
                    "center": f"MATCH (center:{cancer_id}_Gene{{gene_id: '{gene_id}'}}) RETURN center;",
                    "sources": (
                        f"MATCH (center:{cancer_id}_Gene{{gene_id: '{gene_id}'}})\n"
                        f"MATCH (source:{cancer_id}_Gene) -[:REGULATES]-> (regulation:{cancer_id}_Regulation) -[:REGULATED]-> (center)\n"
                        "RETURN  source, regulation"
                    ),
                    "targets": (
                        f"MATCH (center:{cancer_id}_Gene{{gene_id: '{gene_id}'}})\n"
                        f"MATCH (center) -[:REGULATES]-> (regulation:{cancer_id}_Regulation) -[:REGULATED]-> (target:{cancer_id}_Gene)\n"
                        "RETURN  target, regulation"
                    ),
                }
            )
        start = time.time()
        result_map_list = self.get_data_map_list(query_map_list)
        print("Neighborhood transaction time: " + str(time.time() - start))
        return result_map_list

    def get_fraction_map(self, regulation_ids, cancer_id):
        query = (
            f"MATCH (r:{cancer_id}_Regulation)\n"
            f"WHERE r.regulation_id IN {regulation_ids}\n"
            f"RETURN r.regulation_id, r.fraction\n"
        )
        start = time.time()
        fractions = self.get_values(query)
        print("Fraction map transaction time: " + str(time.time() - start))
        return {fraction[0]: fraction[1] for fraction in fractions}

    def get_patients(self, regulation_id, cancer_id):
        query = f"MATCH (patient:{cancer_id}_Patient) -[dysregulation:DYSREGULATED]-> (:{cancer_id}_Regulation {{regulation_id: '{regulation_id}'}}) RETURN patient, dysregulation.value AS dysregulation"
        start = time.time()
        result = self.get_data(query)
        print("Patient transaction time: " + str(time.time() - start))
        return result
    
    def get_all_patient_ids(self, selected_cancer_id):
        query = f"MATCH (p:{selected_cancer_id}_Patient) RETURN DISTINCT p.patient_id;"
        start = time.time()
        result = self.get_data(query)
        print("Patient transaction time: " + str(time.time() - start))
        patient_ids = [value for item in result for value in item.values()]
        options = [{"label": name, "value": name} for name in patient_ids]
        return options

    def get_methylation(self, gene_ids, cancer_id):
        query = (
            f"MATCH (g:{cancer_id}_Gene) WHERE g.gene_id IN {gene_ids}\n"
            f"MATCH (p:{cancer_id}_Patient) -[m:METHYLATED]-> (g)\n"
            f"RETURN g.gene_id, p.patient_id, m.methylation"
        )

        start = time.time()
        result = self.get_values(query)
        print("Methylation transaction time: " + str(time.time() - start))
        return result

    def get_dysregulation(self, regulation_ids, cancer_id):
        query = (
            f"MATCH (r:{cancer_id}_Regulation) WHERE r.regulation_id IN {regulation_ids}\n"
            f"MATCH (p:{cancer_id}_Patient) -[d:DYSREGULATED]-> (r)\n"
            f"RETURN r.regulation_id, p.patient_id, d.value"
        )

        start = time.time()
        result = self.get_values(query)
        print("Dysregulation transaction time: " + str(time.time() - start))
        return result
    
    def get_dysregulation_patient_specific(self, regulation_ids, cancer_id, patient_id):
        query = (
            f"MATCH (r:{cancer_id}_Regulation) WHERE r.regulation_id IN {regulation_ids}\n"
            f"MATCH (p:{cancer_id}_Patient) WHERE p.patient_id = '{patient_id.upper()}'\n"
            f"MATCH (p)-[d:DYSREGULATED]->(r)\n"
            f"RETURN r.regulation_id, p.patient_id, d.value"
        )
        #print(query)
        start = time.time()
        result = self.get_values(query)
        print("Dysregulation patient specific transaction time: " + str(time.time() - start))
        return result

    def get_value(self, command):
        try:
            with self.driver.session() as session:
                return session.run(command).value()
        except Exception as e:
            print("Database problem:")
            print(e)
            return []

    def get_values(self, command):
        with self.driver.session() as session:
            return session.run(command).values()

    def get_data(self, command):
        with self.driver.session() as session:
            result = session.run(command).data()
            return result

    def get_data_map(self, query_map):
        with self.driver.session() as session:
            return {key: session.run(query_map[key]).data() for key in query_map.keys()}

    def get_data_map_list(self, query_map_list):
        with self.driver.session() as session:
            return [
                {key: session.run(query_map[key]).data() for key in query_map.keys()}
                for query_map in query_map_list
            ]
