from genai_infer_service.lib.prompt_template import create_msgs_from_template


mixed = create_msgs_from_template(
    """Hello i am {{name}} my age is {{age}} this is my face {{face}} these are my files {{files}} look at them""",
    {
        "name":"Josh",
        "age":"4"
    },
    {
        "face":5,
        "files":[1,2,3,4,5]
    }
)
print(mixed)
