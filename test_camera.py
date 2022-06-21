
import sys
import cv2
import neoapi

result = 0
try:
    camera1 = neoapi.Cam()
    camera1.Connect()
    camera2 = neoapi.Cam()
    camera2.Connect()

    if camera1.f.PixelFormat.GetEnumValueList().IsReadable('BGR8'):
        camera1.f.PixelFormat.SetString('BGR8')
    elif camera1.f.PixelFormat.GetEnumValueList().IsReadable('Mono8'):
        camera1.f.PixelFormat.SetString('Mono8')
    else:
        print('no supported pixelformat')
        sys.exit(0)

    if camera2.f.PixelFormat.GetEnumValueList().IsReadable('BGR8'):
        camera2.f.PixelFormat.SetString('BGR8')
    elif camera2.f.PixelFormat.GetEnumValueList().IsReadable('Mono8'):
        camera2.f.PixelFormat.SetString('Mono8')
    else:
        print('no supported pixelformat')
        sys.exit(0)
    #camera.f.Width= 640
    #camera.f.Height = 480
    # camera.f.ExposureTime.Set(10000)
    # camera.f.AcquisitionFrameRateEnable.value = True
    # camera.f.AcquisitionFrameRate.value = 10

    while True:
        img1 = camera1.GetImage().GetNPArray()
        title1 = 'Cam 1'
        cv2.namedWindow(title1, cv2.WINDOW_NORMAL)
        cv2.imshow(title1, img1)
        cv2.imwrite('C:/image/1.jpg',img1)

        img2 = camera2.GetImage().GetNPArray()
        title2 = 'Cam 2'
        cv2.namedWindow(title2, cv2.WINDOW_NORMAL)
        cv2.imshow(title2, img2)
        cv2.imwrite('C:/image/2.jpg',img2)

        if cv2.waitKey(1) == 27:
            break

    cv2.destroyAllWindows()


except (neoapi.NeoException, Exception) as exc:
    print('error: ', exc)
    result = 1

sys.exit(result)
