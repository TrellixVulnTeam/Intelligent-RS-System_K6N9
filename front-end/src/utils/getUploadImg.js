import { historyGetPage } from "@/api/history"
import store from "@/store";
import { showFullScreenLoading, hideFullScreenLoading } from "@/utils/loading";
import global from '@/global'
function getUploadImg(type) {
  showFullScreenLoading("#load");
  historyGetPage(1, 20, type).then((res) => {
    hideFullScreenLoading("#load")
    this.beforeImg = res.data.data.map((item) => {
      return { before_img: global.BASEURL + item.before_img };
    });
    this.beforeList=res.data.data.map((item)=>{
      return global.BASEURL + item.before_img
    })
    if (type = '变化检测') {
      this.beforeImg1 = res.data.data.map((item) => {
        return { before_img1: global.BASEURL + item.before_img1 };
      });
    }
    if (type = '目标提取') {
      this.afterList = res.data.data.map((item) => {
        return global.BASEURL + item.after_img;
      })
      this.showingList = res.data.data.map((item) => {
        return global.BASEURL + item.after_img;
      });
      this.lava = res.data.data.map((item)=>{
        return global.BASEURL + item.data[0]
      })
      this.field = res.data.data.map((item)=>{
        return global.BASEURL + item.data[1]
      })
      this.ocean = res.data.data.map((item)=>{
        return global.BASEURL + item.data[2]
      })
      this.desert = res.data.data.map((item)=>{
        return global.BASEURL + item.data[3]
      })
    
      if (this.afterList.length != 0){
        this.goRenderThese(0);
        this.goRenderThis(0);
      }
    }
    this.afterImg = res.data.data.map((item) => {
      return { after_img: global.BASEURL + item.after_img, id: item.id };
    });
    this.checkUpload();
    if(!this.isUpload){
      this.setNormalWay()
    }
  }).then((rej)=>{
    hideFullScreenLoading("#load");
  })
}

function goCompress(type) {
  setTimeout(() => {
    this.$message({
      type: 'info',
      message: "正在压缩，请勿进行其他操作！刷新界面取消压缩",
      duration: 4000,
      center: true,
      showClose: true
    });
  }, 500);
  console.log(type);
  this.historyGetPage(1, 99999, type).then((res) => {

    this.atchDownload(
      res.data.data.map((item) => {
        return { after_img: item.after_img, id: item.id };
      })
    );
  });

  
}

function upload(type) {
  if (this.fileList.length == 0) {
    this.$message.error("请上传图片！");
  } else {
    showFullScreenLoading("#load");
    let formData = new FormData();
    let _this = this;
 
    for (const item of this.fileList) {
      formData.append("files", item) || formData.append('files', item.raw);
      formData.append("type", type);
    }
    this.createSrc(formData).then((res) => {
      this.uploadSrc.list = res.data.data.map((item) => {
        return item.src;
      });
   
      if (type == '目标提取') {
        this.obtainTargetsUpload(this.uploadSrc).then((res) => {
          this.fileList = []
          hideFullScreenLoading("#load")
          this.$message.success("上传成功！");
          this.getMore()
        });
      }
      else if (type == '地物分类') {
        this.classifyUpload(this.uploadSrc).then((res) => {
          this.fileList = []
          hideFullScreenLoading("#load")
          this.$message.success("上传成功！");
          this.getMore()
        });
      }
      else if (type == '目标检测') {
        this.detectTargetsUpload(this.uploadSrc).then((res) => {
          this.fileList = []
          hideFullScreenLoading("#load")
          this.$message.success("上传成功！");
          this.getMore()
        })
      }
      if (this.afterList.length >= 20) {
        this.$confirm("上传图片过多，是否压缩?在此期间不能进行其他操作", "提示", {
          confirmButtonText: "确定",
          cancelButtonText: "取消",
          type: "warning",
        })
          .then(() => {
          
            showFullScreenLoading('#load')
            this.goCompress(type)
          }).catch(() => {
           
          })
      }
      _this.$refs.upload.clearFiles();
    });
  }
}


export { getUploadImg, goCompress, upload }