from kedro.io import DataCatalog
from kedro.pipeline import node, pipeline
from kedro.runner import SequentialRunner


def defrost(frozen_meat):
    return frozen_meat + "_defrosted"


def grill(meat):
    return meat + "_grilled"


def eat(food):
    return food + "_done"


class TestTransformPipelineIntegration:
    def test_connect_existing_pipelines(self):
        """
        Two pipelines exist, the dataset names do not match.
        We `transform` them to work together.
        """
        cook_pipeline = pipeline(
            [node(defrost, "frozen_meat", "meat"), node(grill, "meat", "grilled_meat")]
        )

        lunch_pipeline = pipeline([node(eat, "food", "output")])

        pipeline1 = (
            pipeline(cook_pipeline, outputs={"grilled_meat": "food"}) + lunch_pipeline
        )

        pipeline2 = cook_pipeline + pipeline(
            lunch_pipeline, inputs={"food": "grilled_meat"}
        )
        pipeline3 = pipeline(
            cook_pipeline, outputs={"grilled_meat": "NEW_NAME"}
        ) + pipeline(lunch_pipeline, inputs={"food": "NEW_NAME"})

        for pipe in [pipeline1, pipeline2, pipeline3]:
            catalog = DataCatalog()
            catalog["frozen_meat"] = "frozen_meat_data"
            result = SequentialRunner().run(pipe, catalog)
            output = result["output"].load()
            assert output == "frozen_meat_data_defrosted_grilled_done"

    def test_reuse_same_pipeline(self):
        """
        The same pipeline needs to be used twice in the same big pipeline.
        Normally dataset and node names would conflict,
        so we need to `transform` the pipelines.
        """
        cook_pipeline = pipeline(
            [
                node(defrost, "frozen_meat", "meat", name="defrost_node"),
                node(grill, "meat", "grilled_meat", name="grill_node"),
            ]
        )
        breakfast_pipeline = pipeline([node(eat, "breakfast_food", "breakfast_output")])
        lunch_pipeline = pipeline([node(eat, "lunch_food", "lunch_output")])

        # We are using two different mechanisms here for breakfast and lunch,
        # renaming and prefixing pipelines differently.
        pipe = (
            pipeline(
                cook_pipeline,
                outputs={"grilled_meat": "breakfast_food"},
                namespace="breakfast",
            )
            + breakfast_pipeline
            + pipeline(
                cook_pipeline,
                outputs={"grilled_meat": "lunch_grilled_meat"},
                namespace="lunch",
            )
            + pipeline(lunch_pipeline, inputs={"lunch_food": "lunch_grilled_meat"})
        )
        catalog = DataCatalog()
        catalog["breakfast.frozen_meat"] = "breakfast_frozen_meat"
        catalog["lunch.frozen_meat"] = "lunch_frozen_meat"
        result = SequentialRunner().run(pipe, catalog)
        assert "breakfast_output" in result
        assert "lunch_output" in result
        outputs = {
            "breakfast_output": result["breakfast_output"].load(),
            "lunch_output": result["lunch_output"].load(),
        }

        assert outputs == {
            "breakfast_output": "breakfast_frozen_meat_defrosted_grilled_done",
            "lunch_output": "lunch_frozen_meat_defrosted_grilled_done",
        }
