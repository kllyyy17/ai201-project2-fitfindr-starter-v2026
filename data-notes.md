# FitFindr Data Notes

## Listing fields

A listing has these fields:

- `id` - string
- `title` - string
- `description` - string
- `category` - string
- `style_tags` - list
- `size` - string
- `condition` - string
- `price` - float
- `colors` - list
- `brand` - string or null
- `platform` - string

The fields that will be especially useful for `search_listings` are
`title`, `description`, `category`, `style_tags`, `size`, and `price`.

## Wardrobe fields

A wardrobe item has:

- `id` - string
- `name` - string
- `category` - string
- `colors` - list
- `style_tags` - list
- `notes` - string

These fields will be passed to `suggest_outfit` when generating outfit ideas.

## Example data

- `lst_001`: Vintage Levi's 501 Jeans, W30 L30, $38, bottoms
- `lst_002`: Y2K Baby Tee, S/M, $18, tops
- `lst_003`: Oversized Flannel Shirt, XL, $22, tops
- `lst_004`: 90s Track Jacket, M, $45, outerwear
- `lst_005`: Corduroy Wide-Leg Pants, W28, $32, bottoms
- `lst_006`: Graphic Tee, L, $24, tops

## Starter behavior

The starter runs successfully. The initial agent command:

`python app.py ask 'vintage graphic tee under $30'`

reports that the planning loop has not been built yet and makes 0 model calls. 
This is expected because the tools and planning loop are still stubs.

The example queries also include an empty-search case:

`designer ballgown size XXS under $5`

This will be useful later for testing the required branch where `search_listings` returns no matches.