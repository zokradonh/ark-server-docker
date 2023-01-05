

## How it works

- One container for WebAPI to control the server clusters
- One container per instance
- Each instance container shares the same game files volume
- Each instance has its own SavedArk volume

## Reasons

- One volume per container since there is no good possibility to differ between all the different GameUserSettings.ini of the instances