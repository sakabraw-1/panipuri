select
    hs_code,
    isic_code,
    weight
from {{ ref('hs_to_isic_weights') }}
