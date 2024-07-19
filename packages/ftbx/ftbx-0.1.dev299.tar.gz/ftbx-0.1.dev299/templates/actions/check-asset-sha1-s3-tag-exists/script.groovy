import com.ooyala.flex.plugins.PluginCommand
import com.amazonaws.services.s3.AmazonS3
import com.amazonaws.auth.AWSStaticCredentialsProvider
import com.amazonaws.auth.BasicAWSCredentials
import com.amazonaws.services.s3.AmazonS3ClientBuilder
import com.amazonaws.services.s3.model.GetObjectTaggingRequest

class Script extends PluginCommand {
    def execute() {
        / *
        * Created on: 2024-01-29
        * By: David NAISSE
        * Main steps:
        *   - Build s3 client
        *   - Get sha1 s3 tag
        *   - Return TRUE if sha1 tag exists, else FALSE
        * Changes:
        *   - 
        * /
    
        // vars
        def AWS_KEY = "@[S3_KEY]"
        def AWS_SECRET = "@[S3_SECRET]"
        def AWS_REGION = "@[S3_REGION]"
        def AWS_TAGS = ["computed-sha1", "sha1"]
        def assetId = context.asset.id
        def assetLocation = context.asset.fileInformation.getCurrentLocation()
        def assetBucket = assetLocation.split('/')[2]
        def assetPath = assetLocation.replace("s3://$assetBucket/", "")
        assert assetLocation && assetBucket && assetPath : "Something went wrong while retrieving the asset information. Please try again or contact Dalet support. "
    
        // s3 client
        AmazonS3 s3Client = AmazonS3ClientBuilder.standard()
                .withRegion(AWS_REGION)
                .withCredentials(
                        new AWSStaticCredentialsProvider(
                                new BasicAWSCredentials(AWS_KEY, AWS_SECRET)
                        ))
                .build()
    
        // get s3 tag sha1
        def assetTagRequest = new GetObjectTaggingRequest(assetBucket, assetPath)
        def assetTags = s3Client.getObjectTagging(assetTagRequest).getTagSet()
        def sha1Tag = assetTags.find() { tag -> AWS_TAGS.contains(tag.key) }
    
        // output
        if (sha1Tag) {
            context.logInfo("Found computed-sha1/sha1 s3 tag " + sha1Tag.value + " for asset $assetId.")
            return "TRUE"
        } else {
            context.logInfo("Cannot find computed-sha1/sha1 s3 tag for asset $assetId.")
            return "FALSE"
        }
    }
}