# How to use

`()` = means required  
`[]` = means optional  

1. create a github account  
2. create a repository and make it **private**  
3. **DOUBLE CHECK IF ITS PRIVATE, ITS IMPORTANT!!**  
4. set up secret env:  
    1. Click settings  
    2. on Security sections click secret -> actions  
    3. add new secret by clicking `New repository secret`, then add the following env:  
    ```
        STARTNUMBER=(THE START DATA FOR CURRENT DAILY PERIOD)  inspect element income web, find `data-id` property of first item
        SERVER=(THE SERVER YOU WANT TO SEND)  
        PASSWORD=(YOUR KAGEHERO PASSWORD)  
        USERNAME=(YOUR KAGEHERO EMAIL)  
        DISCORDUSER=(YOUR DISCORD USERID)
        DISCORDTOKEN=[YOUR DISCORD BOT TOKEN FOR NOTIFICATION]
    ```
5. upload all files to github
6. set up workflow folder:
    1. create new file with the following path and name:  
        `.github/workflows/anything.yml`
        you don't need to write anything  
    2. upload all `.yml` files to `.github/workflows/`  by simply clicking `add file` on  
        upper right corner, make sure to check the path  
7. check the running actions by clicking actions tab,  
    look for the orange dot and click  
    if it runs more than 3 minutes, then it is failed else success  
8. to retrigger the workflow, simply add new files or edit, and write nothing then commit  
