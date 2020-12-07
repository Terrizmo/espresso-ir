# Espresso IR

## Introduction

Espresso IR provides the fuctionality to automate memory aquisitions of Windows based EC2 instances and stores them in an S3 bucket. Currently it uses DumpIt to facilitate the memory aquisition part but with some minor edits you could use your tool of choice.

This was created as part of a research paper the author conducted for their MSc dissertaion paper.

Feedback is wanted, collaboration is encouraged. Please do this via the GitHub repositiory.

## Getting Started

use  `pip install espresso-ir` to install the module or clone from this GitHub repositiory <https://github.com/Terrizmo/espresso_ir> and from inside the repository directory run `pip install .`

You must have an account with programatic access to your AWS environment. Once you have the access-key-id and secret-access-key. Once you have this information run `aws configure` and follow the prompt. AWS CLI will store these details in your home directory. These details will then be used each time your run an espresso_ir command. Further infomation can be found in the [AWS documents](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html).

If this is the first time you are running espresso-ir you will need to run the `--setup` flag to create the necessary S3 buckets and to upload DumpIt. The full command it `espresso_ir <case-id> --setup <local-path-to-DumpIt>`

## Requirements

This tool has been designed to use [DumpIt](https://blog.comae.io/your-favorite-memory-toolkit-is-back-f97072d33d5c) by comae. Other memory acquisition tools may be availible in the future.

Finally System manager must be able to communicate with the system manager agent on the EC2 instances you wish to acquire the memory from. You can create the necessary role with the required policies with this tool,  `--setup` flag. Note if you add this role after the the system manager agent has turned on you will need to reboot the agent or the instance to get this functionality. **Rebooting the EC2 instance will lose artifacts in memory, proabably all of them!**

## Acquiring Memory

Once you have completing the instruction in the **Getting Started** section and you have met the **Requirements** you are ready to dump memory from Windows based EC2 instances which will be uplaoaded to your **\<case-id\>-memory-evidence** S3 bucket.

The case ID is a manditory positional argument for espresso-ir and must be the first argument it receives.

It is recommended you turn on API logging in AWS before hand. If you do not have API logging turned on you can use `espresso_ir <case-id> --api-logging`

To start a memory dump you will need the instance ID for each EC2 instance you want to acquire memory from. These currently can only be passed as arguments seperated by a space. for example `espresso_ir <case-id> --dump-memory <instance-id> <instance-id> <instance-id>` . Up to 50 IDs can be passed at once.

## Limitations

At this time you can on dump the memory for 50 EC2 hosts in one CLI entry. This is due to a limitation in the `send command` API. This will be ovecome later using the `Targets` parameter.

This tool only supports DumpIt as the memory acquisition tool.

## TODO

- Next steps
- Features planned
- Known bugs (shortlist)
