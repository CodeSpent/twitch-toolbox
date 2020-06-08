setup(
    name="twitch-clip-manager",
    version="0.0.1",
    description="A CLI tool to manage your Twitch clips in bulk.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/CodeSpent/twitch-clip-manager",
    author="CodeSpent",
    author_email="code@codespent.dev",
    packages=["clip-manager"],
    include_package_data=True,
    entry_points={"console_scripts": ["clip-manager=clip-manager.__main__:main"]},
    datas=[
        ("drivers/geckodriver", "drivers/geckodriver"),
        ("drivers/geckodriver.exe", "drivers/geckodriver.exe"),
    ],
)
