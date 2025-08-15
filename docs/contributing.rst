Contributing Guide
==================

Thank you for your interest in contributing to the PPG Analysis Tool! This guide will help you get started.

How to Contribute
-----------------

Types of Contributions
~~~~~~~~~~~~~~~~~~~~~

We welcome various types of contributions:

* **Bug reports**: Help us identify and fix issues
* **Feature requests**: Suggest new functionality
* **Code contributions**: Submit pull requests with improvements
* **Documentation**: Help improve our docs and examples
* **Testing**: Report bugs or improve test coverage
* **Community support**: Help other users on issues and discussions

Before You Start
----------------

Getting Started
~~~~~~~~~~~~~~

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Set up the development environment** (see :doc:`development`)
4. **Create a branch** for your changes

Communication
~~~~~~~~~~~~~

* **Check existing issues** before creating new ones
* **Use discussions** for questions and feature ideas
* **Be respectful** and constructive in all interactions
* **Follow the project's code of conduct**

Reporting Issues
---------------

Bug Reports
~~~~~~~~~~~

When reporting bugs, please include:

* **Clear description** of the problem
* **Steps to reproduce** the issue
* **Expected vs. actual behavior**
* **Environment details** (OS, Python version, etc.)
* **Error messages** and stack traces
* **Minimal example** that demonstrates the issue

Feature Requests
~~~~~~~~~~~~~~~~

For feature requests, please describe:

* **What you want to achieve**
* **Why this feature is useful**
* **How it should work**
* **Any alternatives you've considered**

Code Contributions
------------------

Code Style
~~~~~~~~~~

* **Follow PEP 8** Python style guidelines
* **Use type hints** where appropriate
* **Write clear, descriptive names** for variables and functions
* **Keep functions focused** and single-purpose
* **Add docstrings** for all public functions and classes

Commit Messages
~~~~~~~~~~~~~~~

Use clear, descriptive commit messages:

* **Use present tense** ("Add feature" not "Added feature")
* **Use imperative mood** ("Move cursor" not "Moves cursor")
* **Limit first line to 50 characters**
* **Add detailed description** after a blank line if needed

Example:
.. code-block:: text

   Add signal quality metrics calculation
   
   - Implement SNR calculation for PPG signals
   - Add peak-to-peak amplitude measurement
   - Include signal variance analysis
   - Update tests to cover new functionality

Pull Request Process
--------------------

Creating Pull Requests
~~~~~~~~~~~~~~~~~~~~~

1. **Ensure your code follows** the project's style guidelines
2. **Write or update tests** for your changes
3. **Update documentation** if needed
4. **Test your changes** thoroughly
5. **Submit a pull request** with a clear description

Pull Request Guidelines
~~~~~~~~~~~~~~~~~~~~~~~

* **Use descriptive titles** that explain the change
* **Include a summary** of what the PR accomplishes
* **Reference related issues** using keywords like "Fixes #123"
* **Add screenshots** for UI changes
* **Include test results** showing your changes work

Review Process
~~~~~~~~~~~~~~

* **All PRs require review** before merging
* **Address feedback** promptly and constructively
* **Be patient** - reviews take time
* **Ask questions** if you don't understand feedback

Testing Requirements
--------------------

Test Coverage
~~~~~~~~~~~~~

* **Maintain test coverage** above 80%
* **Write tests** for all new functionality
* **Update existing tests** when changing behavior
* **Test edge cases** and error conditions

Running Tests
~~~~~~~~~~~~~

Before submitting a PR, ensure:

.. code-block:: bash
   
   # All tests pass
   python -m pytest tests/
   
   # Code coverage is maintained
   python -m pytest tests/ --cov=src --cov-report=html
   
   # No linting errors
   flake8 src/ tests/
   
   # Code is properly formatted
   black --check src/ tests/

Documentation Updates
---------------------

When to Update Docs
~~~~~~~~~~~~~~~~~~~

Update documentation when:

* **Adding new features** or functionality
* **Changing API behavior** or interfaces
* **Fixing bugs** that affect user experience
* **Improving examples** or tutorials

Documentation Standards
~~~~~~~~~~~~~~~~~~~~~~~

* **Use clear, concise language**
* **Include practical examples**
* **Update all related documents**
* **Test documentation builds** locally

Building Documentation
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash
   
   cd docs
   make html
   
   # Check for warnings or errors
   # View the built docs in _build/html/

Code Review Guidelines
----------------------

Reviewing Code
~~~~~~~~~~~~~~

When reviewing code, consider:

* **Functionality**: Does the code do what it's supposed to?
* **Code quality**: Is the code readable and maintainable?
* **Testing**: Are there adequate tests?
* **Documentation**: Is the code well-documented?
* **Performance**: Are there obvious performance issues?
* **Security**: Are there security concerns?

Providing Feedback
~~~~~~~~~~~~~~~~~~

* **Be constructive** and specific
* **Explain the reasoning** behind suggestions
* **Suggest alternatives** when possible
* **Recognize good work** and improvements
* **Ask questions** to understand unclear code

Getting Help
------------

Resources
~~~~~~~~~

* **Project documentation**: Start with the :doc:`user_guide`
* **Development guide**: See :doc:`development` for setup
* **API reference**: Check :doc:`api_reference` for technical details
* **GitHub issues**: Search existing issues and discussions
* **Community chat**: Join our community channels

Asking Questions
~~~~~~~~~~~~~~~~

When asking for help:

* **Search existing issues** first
* **Provide context** about your environment
* **Include error messages** and stack traces
* **Show what you've tried** already
* **Be specific** about what you need help with

Recognition
-----------

Contributor Recognition
~~~~~~~~~~~~~~~~~~~~~~

We appreciate all contributions:

* **Contributors are listed** in the project README
* **Significant contributions** are acknowledged in release notes
* **Community members** are recognized for ongoing support
* **All contributors** are valued regardless of contribution size

Code of Conduct
---------------

Our Standards
~~~~~~~~~~~~~

We are committed to providing a welcoming and inclusive environment:

* **Be respectful** and considerate of others
* **Use inclusive language** and avoid offensive terms
* **Focus on constructive feedback** and collaboration
* **Respect different viewpoints** and experiences
* **Show empathy** towards other community members

Enforcement
~~~~~~~~~~~

* **Unacceptable behavior** will not be tolerated
* **Violations** will be addressed promptly and fairly
* **Consequences** may include warnings or removal from the project
* **Appeals** can be made to project maintainers

Next Steps
----------

Ready to contribute?

1. **Read the development guide** (:doc:`development`)
2. **Set up your environment** and explore the codebase
3. **Start with small issues** labeled "good first issue"
4. **Join discussions** and ask questions
5. **Submit your first contribution**!

Thank you for helping make the PPG Analysis Tool better for everyone!
