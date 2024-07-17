from pydantic import BaseModel
from typing import TypeVar, Any, get_type_hints

T = TypeVar("T", bound=BaseModel)


def is_mutable(model_class):
    current_class = model_class
    while issubclass(current_class, BaseModel):
        if hasattr(current_class, "Config"):
            if hasattr(current_class.Config, "frozen"):
                if current_class.Config.frozen:
                    return False
        current_class = current_class.__base__
    return True


def merge_context(context: T, input: dict[str, Any] | T) -> T:
    """
    Merge the input into the context without mutating the original context. Creates and returns a new instance.
    This function is generic and can handle any subclass of BaseModel.
    Assumptions:
    - the input keys are a subset of the context keys
    - the context may contain some keys that have an Annotated type. If they are Annotated,
      the annotation must be a function that takes the value coming from the context and
      the one from the input, and defines how to merge them.
    """
    if isinstance(input, BaseModel):
        return input.model_copy()
    new_context = context.model_copy()
    annotations = get_type_hints(context.__class__, include_extras=True)
    assert input is not None
    for key, value in input.items():
        if key in annotations:
            annotation = annotations[key]
            if hasattr(annotation, "__metadata__") and annotation.__metadata__:
                # Extract the function from Annotated type
                merge_func = annotation.__metadata__[0]
                setattr(new_context, key, merge_func(getattr(new_context, key), value))
            else:
                setattr(new_context, key, value)
        else:
            # Default behavior for keys without special annotations
            setattr(new_context, key, value)

    return new_context


def update_context(context: BaseModel, input: dict[str, Any] | BaseModel) -> BaseModel:
    input = input.model_dump() if isinstance(input, BaseModel) else input
    return context.model_copy(update=input)


def save_mermaid_to_html(mermaid_code, file_path):
    """
    Saves the provided Mermaid.js code to an HTML file.

    Args:
    mermaid_code (str): The Mermaid.js diagram code.
    file_path (str): Path where the HTML file will be saved.
    """
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mermaid Diagram</title>
        <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
        <script>mermaid.initialize({{startOnLoad:true}});</script>
    </head>
    <body>
        <div class="mermaid">
            {mermaid_code}
        </div>
    </body>
    </html>
    """
    with open(file_path, "w") as file:
        file.write(html_template)
    print(f"Mermaid diagram saved to {file_path}")
