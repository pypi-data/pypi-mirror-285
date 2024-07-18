from time import time
import setuptools
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
setuptools.setup(
    name='abstract_bots',
    version='0.0.0.76',
    author='putkoff',
    author_email='partners@abstractendeavors.com',
    description="This suite of modules not only simplifies the complexities associated with blockchain application development but also ensures high levels of performance and security. By providing tools for detailed data handling, transaction analysis, and secure blockchain interactions, these modules form a comprehensive solution ideal for developers looking to build or maintain advanced Solana-based applications.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/AbstractEndeavors/abstract_ai',
    classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.11',
      ],
    install_requires=['requests','solders','solana','base58','sqlalchemy','abstract_security','python-dotenv','abstract_utilities'],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    # Add this line to include wheel format in your distribution
    setup_requires=['wheel'],
)
