.. _dev_env:

*********************
Developer Environment
*********************

This Python package is used in the pipeline processing of scientific data from SWcSOC affiliated missions.
Special consideration is therefore required to ensure that development is compatible with the pipeline environment.
It is also important to ensure that this package is compatible with a user's systems such as a mac and windows.

Visual Studio Code
==================
Though not required, this packate designed for development in `Visual Studio Code <https://code.visualstudio.com/>`_ inside of a container managed by Docker.
This is the same environment that is used by the data processing pipeline.
All of the configuration required by VS Code are maintained in the `.devcontainer` folder including the Dockerfile.
For more information see `Developing inside a Container <https://code.visualstudio.com/docs/remote/containers>`.

Setup
^^^^^
Follow these steps to set up VS Code.

#. Download and install `VS Code <https://code.visualstudio.com/>`_.
#. Download and install Docker. The easiest way to do that is to install `Docker Desktop <https://www.docker.com/products/docker-desktop/>`_.
#. Open VS Code and add the following 2 extensions by navigating to View->Extensions.
    #. Docker
    #. Remote-Container
#. Ensure that Docker is running by opening Docker Desktop. It will be required to build the container.
#. Restart VS Code and open this repository using File->Open Folder. It might recognize that a container is defined and prompt you to Reopen in Container. Do so.
#. If not, open the VS Code Command Palette by View->Command Palette (or Ctrl+Shift+P) and select: "Remote-Containers:Rebuild and Reopen in Container"
#. VS Code should build and open the container (takes as much as 10-20 minutes the first time). You will see “Starting Dev Container (show log): Building image” in the bottom right corner. Click on “show log” to see details of the build. This requires Docker to be running.
#. Once the build has finished, you will see information about the Dev Container in the bottom left.
#. Exiting VS Code will close the docker container.
#. The next time you open this folder with VS Code it should open in the built container. It should not have to rebuild the container unless the Dockerfile file has changed.

