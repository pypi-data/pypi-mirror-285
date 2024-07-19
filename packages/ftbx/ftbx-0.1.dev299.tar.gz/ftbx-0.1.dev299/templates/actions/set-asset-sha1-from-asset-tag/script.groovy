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
        *   - get asset sha1 tags
        *   - set sha1 to asset.metadata.general-info.sha1
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
        def assetMetadata = services.assetService.getAssetMetadata(assetId)
        assert assetLocation && assetBucket && assetPath && assetMetadata : "Something went wrong while retrieving the asset information. Please try again or contact Dalet support. "
    
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
        assert sha1Tag
    
        // output
        context.logInfo("About to set sha1 " + sha1Tag.value + " on assetId $assetId...")
        assetMetadata.getField("general-info").getField("sha1").setValue(sha1Tag.value)
        services.assetService.setAssetMetadata(assetId, assetMetadata)
        context.logInfo("Successfully updated assetId $assetId metadata. ")
    }
}