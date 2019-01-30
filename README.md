# WebRTC Scripts

These scripts are used for preparing the development environment, building, and creating WebRTC NuGet packages for the Universal Windows Platform (UWP). The Chromium platform flag used for UWP is `winuwp`.

**Requirements (Windows 10)**
>Note: The below requirements apply only to running the Python scripts. Compiling the binaries has additional requirements which are listed in the [webrtc-uwp-sdk](https://github.com/webrtc-uwp/webrtc-uwp-sdk) repo.
- Visual Studio 2017 or VS Code
- Python 2.7 (Scripts supports Python 3 too, but Google's build system for WebRtc doesn't)
- Strawberry Perl (Supported perl version can be obrained from http://strawberryperl.com/)

## Getting Started
The simplest way to build WebRTC which doesn't require familiarizing yourself with the scripts and how to pass input arguments is opening the `webrtc-uwp-sdk\webrtc\windows\solutions\WebRtc.Universal.sln` solution and building the Org.Ortc project. This way the WebRTC environment for winuwp will be prepared and built for selected cpu and configuration. You can immediately try it by compiling and running PeerConnectionClient.WebRtc project for a sample app that demonstrates audio\video calls.

## Python Preparation Scripts
These scripts are new so we expect there to be some rough edges - please log any issues on GitHub. If you are eager to try it, you can just run the `run.py` Python script from scripts folder. It can be run from any folder on your disk. (i.e. e:\my_working>python d:\test\webrtc-uwp-sdk\scripts\run.py). The folder from which run.py is called will be the working directory and the file `userdef.py` which contains the default values will be created there. This file can be edited to modify the default actions and platforms. For further details see the section "How to pass input args?"

By running this line of code:
>python run.py
	
the development environment will be prepared for win and winuwp platforms, for ARM, x86 and x64 CPUs and for debug and release configurations. In summary, the build system will pe prepared for all supported combinations. After the preparation process is finished the same script will proceed with building WebRTC for all combinations that were prepared successfully. That will take at least 2 hours. So be patient, or read on for information on specifying the platforms to prepare.

## Python Script Configuration

### How to prepare developement environment

Before you are able to build the WebRTC projects it is required to prepare the development environemnt. To do that, run the `run.py` Python script with the 'prepare' parameter. The script will download and install missing tools. It will create junction links in the directory structure and copy files to the proper locations.  It will also generate ninja files and Visual Studio projects. The folder where these generated files will be saved is: 

>`webrtc-uwp-sdk\webrtc\xplatform\webrtc\out\webrtc_[platform]_[cpu]_[configuration]`
(e.g. `webrtc-uwp-sdk\webrtc\xplatform\webrtc\out\webrtc_winuwp_x86_Release`)
	
## Examples for preparing the development environment

1. The easiest way for those who don't want to play with scripts and are interested in specific cpu and configuration is to open `webrtc-uwp-sdk\webrtc\windows\solutions\WebRtc.Universal.sln` and to build Org.WebRtc project. This won't just prepare environemnt but it will build the wrapper project too.

2. If you want to prepare the environment for all platforms and CPUs and configurations, without building, you can run following command:
    >`python run.py -a prepare`

    This line can be used if you running this from scripts folder, otherwise you need to specify full or relative path to the run.py script. The result of prepare action can be found in the `webrtc-uwp-sdk\webrtc\xplatform\webrtc\out\` folder.
  
    In case you want to prepare the environment for specific CPUs and configuration the next command will do the job:
    >`python run.py -a prepare --cpus x64 arm -c debug`
	
3. If you want to have even more control over script execution, modifying userdef.py file is right solution for you. First what you need to do is to create that file. To do that it is enough to run: 
    >`python run.py -a createuserdef`
  
    Once userdef.py is created you can start making modifications. That file is created using `default.py` as template. Every option has comments that describes available values and their use.

    **Configuration Example:** Build WebRTC and backup the results of that build for win and winuwp platforms, but only for x64 and release. Your setup should look like this:
    ```
    targets = [ 'webrtc' ]
    targetCPUs = [ 'x64' ]
    targetPlatforms = [ 'win', 'winuwp' ]
    targetConfigurations = [ 'Release' ]
    actions = [ 'prepare', 'build', 'backup' ]
    ```
  
    If you don't run the action to create the `userdef.py` file, the script will be generated automatically. In case you want to reset `userderf.py` to its defaults just run the action `createuserdef` again, or delete the file and run preparation.
  
    If you are satisfied with your changes in userdef.py file and you want to keep it for future use, you can copy that file to `webrtc-uwp-sdk\scripts\templates` folder and name it as you wish.
  This leads us to fourth way of passing input arguments.
  
4. By creating templates and placing them in the`webrtc-uwp-sdk\scripts\templates` folder you are getting a new option for passing input arguments. The best way to create a template is to use the `userdef.py` file as reference. Once you modify variables that are of interest, you can delete rest of them and save it to a template file.
  
    Running the script with the template file looks like this:

    >```python run.py template_file.py ```

    or 
    >```python run.py template_file```
    
    By creating templates for the most common actions you can simplify running scripts.

## Release Notes  
Creating release notes process can be done by running releasenotes action, which can be run in two ways:
1. By running the following command:
>```python run.py -a releasenotes```
2. Or by adding 'releasenotes' action into `actions` variable inside userdef.py and running the command: 
>```python run.py```

By following the instruction in the console you will be able to choose a way to insert the release notes, either by typing it directly in the cmd window or by selecting notes from a file (selecting from a file copies files contents and from them creates a release note.)

Release notes are stored in **releases.txt** file inside root sdk directory

Version of the release notes will be added automaticly when running `publishnuget` action, or it can be added manualy by adding in `--setservernoteversion` option when you next time you call the `python run.py` command, which will take latest published version of the nuget package and set it as a release note version.

## Creating NuGet package  
Creating NuGet package for WebRtc UWP can be done by running createnuget action.  

1. Prefered way to do this is to insert 'createnuget' into actions variable inside userdef.py file and set up    the configuration.  
   **Configuration Example:** Create WebRtc NuGet package for WinUWP platform for x64 release version:
   ```
    targets = [ 'webrtc' ]
    targetCPUs = [ 'x64' ]
    targetPlatforms = [ 'winuwp' ]
    targetConfigurations = [ 'Release' ]
    actions = [ 'createnuget' ]
   ```
   *If the prepare and build actions for the selected configuration have not been done before running createnuget action, action variable should have those actions as well in order for the nuget creation process to succeed.* 
   example: ``` actions = [ 'prepare', 'build', 'createnuget' ]```   
   After configuration has been setup, run the following command:   
   >```python run.py ```  

2. All of this can also be done by running the following command:  
   >```python run.py -a createnuget <configuration>```   
   
   ---
   **Configuration**  
   
   Platforms: `-t winuwp`  
   Cpu architectures: `-x x64 x86 arm`  
   Configuration: `-c debug release`   
   
   **Command Example:**  Create WebRtc NuGet package for WinUWP platform for x64 release version:
   >```python run.py -a createnuget -t winuwp -x x64 -c release```  
   *Assuming the prepare and build has been done beforehand*
   
   ---
To select nuget package version, change the `nugetVersionInfo` variable in userdef.py, this variable is used for WebRtc versions that already have published packages, in which case, next package version will be selected automatically.
To create a NuGet package for a WebRtc version that does not have a published nuget package on nuget.org, use `manualNugetVersionNumber` variable in userdef.py to manually add in a version of the nuget package, for example:
>manualNugetVersionNumber = '1.71.0.1-Alpha'

To select a directory where the newly created NuGet packages will be placed, change the value of the `nugetFolderPath` variable inside userdef.py to a path of your choosing.
