# Copyright (C) 2022 Alteryx, Inc. All rights reserved.
#
# Licensed under the ALTERYX SDK AND API LICENSE AGREEMENT;
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.alteryx.com/alteryx-sdk-and-api-license-agreement
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Large number calculator tool."""
from decimal import Decimal, InvalidOperation, localcontext

import pyarrow as pa
from ayx_python_sdk.core import (
    Anchor,
    PluginV2,
)
from ayx_python_sdk.providers.amp_provider.amp_provider_v2 import AMPProviderV2
from ayx_python_sdk.providers.amp_provider.builders.metadata_builder import MetadataBuilder

class LargeNumberCalculator(PluginV2):
    """Calculate two string fields without converting them to machine integers."""

    def __init__(self, provider: AMPProviderV2):
        """Construct the plugin."""
        self.name = "LargeNumberCalculator"
        self.provider = provider
        self.provider.io.info(f"{self.name} tool started")
        self._push_output_metadata()

    def _push_output_metadata(self, input_schema=None) -> None:
        """Publish the output schema during update-only mode and record processing."""
        result_field = self.provider.tool_config.get("resultField", "")
        if not result_field:
            return

        if input_schema is not None:
            fields = list(input_schema)
        else:
            input_connections = self.provider.incoming_anchors.get("Input", {})
            if not input_connections:
                return
            input_metadata = next(iter(input_connections.values())).get("metadata")
            if input_metadata is None:
                return
            metadata = MetadataBuilder.from_protobuf(input_metadata)
            fields = [field.to_arrow() for field in metadata]

        result = pa.field(result_field, pa.string())
        result_index = next((index for index, field in enumerate(fields) if field.name == result_field), None)
        if result_index is None:
            fields.append(result)
        else:
            fields[result_index] = result
        self.provider.push_outgoing_metadata("Output", pa.schema(fields))

    def on_record_batch(self, batch: "pa.Table", anchor: Anchor) -> None:
        """
        Process the passed record batch.

        The method that gets called whenever the plugin receives a record batch on an input.

        This method IS NOT called during update-only mode.

        Parameters
        ----------
        batch
            A pyarrow Table containing the received batch.
        anchor
            A namedtuple('Anchor', ['name', 'connection']) containing input connection identifiers.
        """
        configuration = self.provider.tool_config
        first_field = configuration.get("firstField", "")
        second_field = configuration.get("secondField", "")
        operator = configuration.get("operator", "+")
        result_field = configuration.get("resultField", "")

        if operator not in {"+", "-", "*", "/"}:
            self.provider.io.error(f"Unsupported operator: {operator}")
            return
        if not first_field or not second_field or not result_field:
            self.provider.io.error("Two input fields and a result field are required.")
            return
        if first_field not in batch.column_names or second_field not in batch.column_names:
            self.provider.io.error("Configured input field was not found in the input data.")
            return

        try:
            results = [
                self._calculate(first, second, operator)
                for first, second in zip(
                    batch[first_field].to_pylist(), batch[second_field].to_pylist()
                )
            ]
        except (InvalidOperation, ValueError, ZeroDivisionError) as error:
            self.provider.io.error(f"Could not calculate large number field: {error}")
            return

        result_array = pa.array(results, type=pa.string())
        self._push_output_metadata(batch.schema)
        if result_field in batch.column_names:
            result_index = batch.column_names.index(result_field)
            output = batch.set_column(result_index, result_field, result_array)
        else:
            output = batch.append_column(result_field, result_array)
        self.provider.write_to_anchor("Output", output)

    @staticmethod
    def _calculate(first: object, second: object, operator: str) -> str:
        if first is None or second is None:
            return None

        first_text = str(first).strip()
        second_text = str(second).strip()
        precision = max(len(first_text), len(second_text)) * 2 + 50
        with localcontext() as context:
            context.prec = max(50, precision)
            left = Decimal(first_text)
            right = Decimal(second_text)
            if operator == "+":
                result = left + right
            elif operator == "-":
                result = left - right
            elif operator == "*":
                result = left * right
            else:
                result = left / right

        result_text = format(result, "f")
        if "." in result_text:
            result_text = result_text.rstrip("0").rstrip(".")
        return result_text or "0"

    def on_incoming_connection_complete(self, anchor: Anchor) -> None:
        """
        Call when an incoming connection is done sending data including when no data is sent on an optional input anchor.

        This method IS NOT called during update-only mode.

        Parameters
        ----------
        anchor
            NamedTuple containing anchor.name and anchor.connection.
        """
        self.provider.io.info(
            f"Received complete update from {anchor.name}:{anchor.connection}."
        )

    def on_complete(self) -> None:
        """
        Clean up any plugin resources, or push records for an input tool.

        This method gets called when all other plugin processing is complete.

        In this method, a Plugin designer should perform any cleanup for their plugin.
        However, if the plugin is an input-type tool (it has no incoming connections),
        processing (record generation) should occur here.

        Note: A tool with an optional input anchor and no incoming connections should
        also write any records to output anchors here.
        """
        self.provider.io.info(f"{self.name} tool done.")
