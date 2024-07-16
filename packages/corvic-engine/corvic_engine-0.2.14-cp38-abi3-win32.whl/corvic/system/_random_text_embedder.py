import numpy as np
import polars as pl

from corvic.system._embedder import EmbedTextContext, EmbedTextResult, TextEmbedder


class RandomTextEmbedder(TextEmbedder):
    """Embed inputs by choosing random vectors.

    Useful for testing.
    """

    def embed(self, context: EmbedTextContext) -> EmbedTextResult:
        rng = np.random.default_rng()

        match context.expected_coordinate_bitwidth:
            case 64:
                coord_dtype = pl.Float64()
            case 32:
                coord_dtype = pl.Float32()

        return EmbedTextResult(
            context=context,
            embeddings=pl.Series(
                rng.random(size=(len(context.inputs), context.expected_vector_length)),
                dtype=pl.Array(
                    coord_dtype,
                    width=context.expected_vector_length,
                ),
            ),
        )
